function StudioEditableXBlock(runtime, element) {
    "use strict";

    var fields = [];
    var tinyMceAvailable = (typeof $.fn.tinymce !== 'undefined'); // Studio includes a copy of tinyMCE and its jQuery plugin
    var datepickerAvailable = (typeof $.fn.datepicker !== 'undefined'); // Studio includes datepicker jQuery plugin

    $(element).find('.field-data-control').each(function() {
        var $field = $(this);
        var $wrapper = $field.closest('li');
        var $resetButton = $wrapper.find('button.setting-clear');
        var type = $wrapper.data('cast');
        fields.push({
            name: $wrapper.data('field-name'),
            isSet: function() { return $wrapper.hasClass('is-set'); },
            hasEditor: function() { return tinyMceAvailable && $field.tinymce(); },
            val: function() {
                var val = $field.val();
                // Cast values to the appropriate type so that we send nice clean JSON over the wire:
                if (type == 'boolean')
                    return (val == 'true' || val == '1');
                if (type == "integer")
                    return parseInt(val, 10);
                if (type == "float")
                    return parseFloat(val);
                if (type == "generic" || type == "list" || type == "set") {
                    val = val.trim();
                    if (val === "")
                        val = null;
                    else
                        val = JSON.parse(val); // TODO: handle parse errors
                }
                return val;
            },
            removeEditor: function() {
                $field.tinymce().remove();
            }
        });
        var fieldChanged = function() {
            // Field value has been modified:
            $wrapper.addClass('is-set');
            $resetButton.removeClass('inactive').addClass('active');
        };
        $field.bind("change input paste", fieldChanged);
        $resetButton.click(function() {
            $field.val($wrapper.attr('data-default')); // Use attr instead of data to force treating the default value as a string
            $wrapper.removeClass('is-set');
            $resetButton.removeClass('active').addClass('inactive');
        });
        if (type == 'html' && tinyMceAvailable) {
            tinyMCE.baseURL = baseUrl + "/js/vendor/tinymce/js/tinymce";
            $field.tinymce({
                theme: 'modern',
                skin: 'studio-tmce4',
                height: '200px',
                formats: { code: { inline: 'code' } },
                codemirror: { path: "" + baseUrl + "/js/vendor" },
                convert_urls: false,
                plugins: "link codemirror",
                menubar: false,
                statusbar: false,
                toolbar_items_size: 'small',
                toolbar: "formatselect | styleselect | bold italic underline forecolor wrapAsCode | bullist numlist outdent indent blockquote | link unlink | code",
                resize: "both",
                setup : function(ed) {
                    ed.on('change', fieldChanged);
                }
            });
        }

        if (type == 'datepicker' && datepickerAvailable) {
            $field.datepicker('destroy');
            $field.datepicker({dateFormat: "m/d/yy"});
        }
    });

    $(element).find('.wrapper-list-settings .list-set').each(function() {
        var $optionList = $(this);
        var $checkboxes = $(this).find('input');
        var $wrapper = $optionList.closest('li');
        var $resetButton = $wrapper.find('button.setting-clear');

        fields.push({
            name: $wrapper.data('field-name'),
            isSet: function() { return $wrapper.hasClass('is-set'); },
            hasEditor: function() { return false; },
            val: function() {
                var val = [];
                $checkboxes.each(function() {
                    if ($(this).is(':checked')) {
                        val.push(JSON.parse($(this).val()));
                    }
                });
                return val;
            }
        });
        var fieldChanged = function() {
            // Field value has been modified:
            $wrapper.addClass('is-set');
            $resetButton.removeClass('inactive').addClass('active');
        };
        $checkboxes.bind("change input", fieldChanged);

        $resetButton.click(function() {
            var defaults = JSON.parse($wrapper.attr('data-default'));
            $checkboxes.each(function() {
                var val = JSON.parse($(this).val());
                $(this).prop('checked', defaults.indexOf(val) > -1);
            });
            $wrapper.removeClass('is-set');
            $resetButton.removeClass('active').addClass('inactive');
        });
    });

    var studio_submit = function(data) {
        var handlerUrl = runtime.handlerUrl(element, 'submit_studio_edits');
        runtime.notify('save', {state: 'start', message: gettext("Saving")});
        $.ajax({
            type: "POST",
            url: handlerUrl,
            data: JSON.stringify(data),
            dataType: "json",
            global: false,  // Disable Studio's error handling that conflicts with studio's notify('save') and notify('cancel') :-/
            success: function(response) { runtime.notify('save', {state: 'end'}); }
        }).fail(function(jqXHR) {
            var message = gettext("This may be happening because of an error with our server or your internet connection. Try refreshing the page or making sure you are online.");
            if (jqXHR.responseText) { // Is there a more specific error message we can show?
                try {
                    message = JSON.parse(jqXHR.responseText).error;
                    if (typeof message === "object" && message.messages) {
                        // e.g. {"error": {"messages": [{"text": "Unknown user 'bob'!", "type": "error"}, ...]}} etc.
                        message = $.map(message.messages, function(msg) { return msg.text; }).join(", ");
                    }
                } catch (error) { message = jqXHR.responseText.substr(0, 300); }
            }
            runtime.notify('error', {title: gettext("Unable to update settings"), message: message});
        });
    };

    $('.save-button', element).bind('click', function(e) {
        e.preventDefault();
        var values = {};
        var notSet = []; // List of field names that should be set to default values
        for (var i in fields) {
            var field = fields[i];
            if (field.isSet()) {
                values[field.name] = field.val();
            } else {
                notSet.push(field.name);
            }
            // Remove TinyMCE instances to make sure jQuery does not try to access stale instances
            // when loading editor for another block:
            if (field.hasEditor()) {
                field.removeEditor();
            }
        }
        studio_submit({values: values, defaults: notSet});
    });

    $(element).find('.cancel-button').bind('click', function(e) {
        // Remove TinyMCE instances to make sure jQuery does not try to access stale instances
        // when loading editor for another block:
        for (var i in fields) {
            var field = fields[i];
            if (field.hasEditor()) {
                field.removeEditor();
            }
        }
        e.preventDefault();
        runtime.notify('cancel', {});
    });

    // Raccoongang addons

    var languages = [];
    var $fileUploader = $('.input-file-uploader', element);
    var $langChoicer = $('.lang-choiser', element);
    var setLanguages = $('input[data-field-name="transcripts"]').val();

    if(setLanguages){
        languages = JSON.parse(setLanguages);
    }
    var pushLanguage = function (lang, label, url){
        var indexLanguage;
        for (var i=0; i < languages.length; i++){
            if (lang == languages[i].lang){
                indexLanguage = i
            }
        }
        if (indexLanguage !== undefined){
            languages[indexLanguage].url = url
        } else {
            languages.push({
                lang: lang,
                url: url,
                label: label
            })
        }
        $('.add-transcript').removeClass('is-disabled');
    };

    var clickUploader = function(event){
        event.preventDefault();
        event.stopPropagation();
        var $buttonBlock = $(event.currentTarget);
        $fileUploader.data({
            'lang-code': $buttonBlock.data('lang-code'),
            'lang-label': $buttonBlock.data('lang-label'),
            'change-field-name': $buttonBlock.data('change-field-name')
        });
        $fileUploader.attr({
            'data-lang-code': $buttonBlock.data('lang-code'),
            'data-lang-label': $buttonBlock.data('lang-label'),
            'data-change-field-name': $buttonBlock.data('change-field-name')
        });

        $fileUploader.click();
    };

    var languageChecker = function (event) {
        event.stopPropagation();
        var $selectedOption = $(event.currentTarget).find('option:selected');
        var selectedLanguage = $selectedOption.val();
        var languageLabel = $selectedOption.data('lang-label');
        var $langSelectParent = $(event.currentTarget).parent('li');
        var $input = $('.upload-transcript', $langSelectParent);
        var oldLang = $input.data('lang-code');
        if(selectedLanguage){
            if(selectedLanguage != oldLang){
                for(var i=0; i < languages.length; i++){
                    if(languages[i].lang == oldLang){
                        languages[i].lang = selectedLanguage;
                        languages[i].label = languageLabel
                    }
                }
            }
            $input.data({
                'lang-code': selectedLanguage,
                'lang-label': languageLabel
            });
            $input.attr({
                'data-lang-code': selectedLanguage,
                'data-lang-label': languageLabel
            });
            $input.removeClass('is-hidden');
        } else {
            $input.data({
                'lang-code': '',
                'lang-label': ''
            });
            $input.attr({
                'data-lang-code': '',
                'data-lang-label': ''
            });
            $input.addClass('is-hidden');
        }
        $('input[data-field-name="transcripts"]').val(JSON.stringify(languages)).change();
    };

    $fileUploader.on('change', function(event) {
        var fieldName = $(event.currentTarget).data('change-field-name');
        var lang = $(event.currentTarget).data('lang-code');
        var label = $(event.currentTarget).data('lang-label');
        $('.file-uploader-form', element).ajaxSubmit({
            success: function(response, statusText, xhr, form) {
                if(lang == ""){
                    $('input[data-field-name=' + fieldName + ']').val(response['asset']['id']).change();
                } else {
                    pushLanguage(lang, label, '/' + response['asset']['id']);
                    $('input[data-field-name=' + fieldName + ']').val(JSON.stringify(languages)).change();
                }
                $(event.currentTarget).removeData();
                $(event.currentTarget).attr({
                    'data-change-field-name': '',
                    'data-lang-code': '',
                    'data-lang-label': ''
                });
            }
        });
    });

    $('.add-transcript', element).on('click', function (event) {
        event.preventDefault();
        $(event.currentTarget).addClass('is-disabled');
        var $choiserItem = $('.list-settings-item:hidden').clone();
        $choiserItem.removeClass('is-hidden');
        $choiserItem.appendTo($langChoicer);
        $('.upload-transcript', $choiserItem).on('click', clickUploader);
        $('.lang-select', $choiserItem).on('change', languageChecker);
    });

    $('.lang-select').on('change', languageChecker);

    $('.upload-transcript, .upload-action', element).on('click', clickUploader);

    $(document).on('click', '.remove-action', function(event){
        event.preventDefault();
        event.stopPropagation();
        var $currentBlock = $(event.currentTarget).closest('li');
        var lang = $currentBlock.find('option:selected').val();
        for (var i=0; i < languages.length; i++){
            if(lang == languages[i].lang){
                languages.splice(i,1)
            }
        }
        if(!languages.length){
            $currentBlock.parents('li').removeClass('is-set');
            $currentBlock.parents('li').find('.setting-clear').removeClass('active').addClass('inactive');
        }
        $currentBlock.remove();
        $('input[data-field-name="transcripts"]').val(JSON.stringify(languages)).change();

    });
    // End of Raccoongang addons
}
