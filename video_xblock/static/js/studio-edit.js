/**
    StudioEditableXBlock function for setting up the Video xblock.
    This function was copied from xblock-utils by link
        https://github.com/edx/xblock-utils/blob/master/xblockutils/templates/studio_edit.html
    and extended by Raccoon Gang company
    It is responsible for a validating and sending data to backend
*/
function StudioEditableXBlock(runtime, element) {
    'use strict';

    var fields = [];
    // Studio includes a copy of tinyMCE and its jQuery plugin
    var tinyMceAvailable = (typeof $.fn.tinymce !== 'undefined');  // TODO: Remove TinyMCE
    var datepickerAvailable = (typeof $.fn.datepicker !== 'undefined'); // Studio includes datepicker jQuery plugin

    /** This function is used for Brightcove HLS debugging
     *  profile: ingest profile to use for re-transcode job.
     *  Accepted values: default, autoquality, encryption.
     */

    var uiDispatch = function uiDispatch(method, suffix) {
        return $.ajax({
            type: method,
            url: runtime.handlerUrl(element, 'ui_dispatch', suffix),
            data: '{}'
        });
    };

    var dispatch = function dispatch(method, suffix) {
        return $.ajax({
            type: method,
            url: runtime.handlerUrl(element, 'dispatch', suffix),
            data: '{}'
        });
    };

    var submitBCReTranscode = function submitBCReTranscode(profile) {
        $.when(
            dispatch('POST', 'submit_retranscode_' + profile)
        ).then(function(response) {
            $('#brightcove-retranscode-status').html(
                'Your retranscode request was successfully submitted to Brightcove VideoCloud. ' +
                'It takes few minutes to process it. Job id ' + response.id);
        });
    };

    var bcLoadVideoTechInfo = function bcLoadVideoTechInfo() {
        $.when(
            dispatch('POST', 'get_video_tech_info')
        ).then(function(response) {
            $('#bc-tech-info-renditions').html(response.renditions_count);
            $('#bc-tech-info-autoquality').html(response.auto_quality);
            $('#bc-tech-info-encryption').html(response.encryption);
        });
    };

    var getReTranscodeStatus = function getReTranscodeStatus() {
        $.when(
            dispatch('POST', 'retranscode-status')
        ).then(function(data) {
            $('#brightcove-retranscode-status').html(data);
        });
    };

    var showBackendSettings = function showBackendSettings() {
        $.when(
            uiDispatch('GET', 'can-show-backend-settings')
        ).then(function(response) {
            if (response.data.canShow) {
                $('#brightcove-advanced-settings').toggleClass('is-hidden', false);
                bcLoadVideoTechInfo();
                getReTranscodeStatus();
            }
        });
    };

    $('#submit-re-transcode').click(function() {
        var profile = $('#xb-field-edit-retranscode-options').val();
        submitBCReTranscode(profile);
    }
    );

    $('#settings-tab').ready(function() {
        showBackendSettings();
    });

    $(element).find('.field-data-control').each(function() {
        var $field = $(this);
        var $wrapper = $field.closest('li');
        var $resetButton = $wrapper.find('button.setting-clear');
        var type = $wrapper.data('cast');
        var contextId = $wrapper.context.id;
        fields.push({
            name: $wrapper.data('field-name'),
            isSet: function() { return $wrapper.hasClass('is-set'); },
            hasEditor: function() { return tinyMceAvailable && $field.tinymce(); },
            val: function() {
                var val = $field.val();
                // Cast values to the appropriate type so that we send nice clean JSON over the wire:
                if (type == 'boolean') {  // eslint-disable-line
                    return (val == 'true' || val == '1');  // eslint-disable-line
                }
                if (type == 'integer') {  // eslint-disable-line
                    return parseInt(val, 10);
                }
                if (type == 'float') {  // eslint-disable-line
                    return parseFloat(val);
                }
                if (type == 'generic' || type == 'list' || type == 'set') {  // eslint-disable-line
                    val = val.trim();
                    if (val === '') {
                        val = null;
                    } else {
                        val = JSON.parse(val); // TODO: handle parse errors
                    }
                    return val;
                }
                /* eslint-disable */
                if (type == 'string' && (
                    contextId == 'xb-field-edit-start_time'
                    || contextId == 'xb-field-edit-end_time')) {
                    return parseRelativeTime(val);
                }
                /* eslint-disable */
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
        $field.bind('change input paste', fieldChanged);
        $resetButton.click(function() {
            $field.val($wrapper.attr('data-default')); // Use attr instead of data to force treating the default value as a string
            $wrapper.removeClass('is-set');
            $resetButton.removeClass('active').addClass('inactive');
        });
        if (type == 'html' && tinyMceAvailable) {
            tinyMCE.baseURL = baseUrl + '/js/vendor/tinymce/js/tinymce';
            $field.tinymce({
                theme: 'modern',
                skin: 'studio-tmce4',
                height: '200px',
                formats: { code: { inline: 'code' } },
                codemirror: { path: "" + baseUrl + '/js/vendor' },
                convert_urls: false,
                plugins: 'link codemirror',
                menubar: false,
                statusbar: false,
                toolbar_items_size: 'small',
                toolbar: 'formatselect | styleselect | bold italic underline forecolor wrapAsCode | bullist numlist outdent indent blockquote | link unlink | code',
                resize: 'both',
                setup : function(ed) {
                    ed.on('change', fieldChanged);
                }
            });
        }

        if (type == 'datepicker' && datepickerAvailable) {
            $field.datepicker('destroy');
            $field.datepicker({dateFormat: 'm/d/yy'});
        }
    });

    $(element).find('.wrapper-list-settings .list-set').each(function() {
        var $optionList = $(this);
        var $checkboxes = $(this).find('input');
        var $wrapper = $optionList.closest('li');
        var $resetButton = $wrapper.find('button.setting-clear');
        var fieldChanged = function() {
            // Field value has been modified:
            $wrapper.addClass('is-set');
            $resetButton.removeClass('inactive').addClass('active');
        };

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
        $checkboxes.bind('change input', fieldChanged);

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
        runtime.notify('save', {state: 'start', message: gettext('Saving')});
        $.ajax({
            type: 'POST',
            url: handlerUrl,
            data: JSON.stringify(data),
            dataType: 'json',
            global: false,  // Disable Studio's error handling that conflicts with studio's notify('save') and notify('cancel') :-/
            success: function(response) { runtime.notify('save', {state: 'end'}); }
        }).fail(function(jqXHR) {
            var message = gettext('This may be happening because of an error with our server or your internet connection. Try refreshing the page or making sure you are online.');
            if (jqXHR.responseText) { // Is there a more specific error message we can show?
                try {
                    message = JSON.parse(jqXHR.responseText).error;
                    if (typeof message === 'object' && message.messages) {
                        // e.g. {"error": {"messages": [{"text": "Unknown user 'bob'!", "type": "error"}, ...]}} etc.
                        message = $.map(message.messages, function(msg) { return msg.text; }).join(", ");
                    }
                } catch (error) { message = jqXHR.responseText.substr(0, 300); }
            }
            runtime.notify('error', {title: gettext('Unable to update settings'), message: message});
        });
    };

    // Raccoongang changes

    var fillValues = function (e) {
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
    };

    var validateTranscripts = function(e) {
        e.preventDefault();
        var isValid = [];
        var $visibleLangChoiceItems = $langChoiceItem.find('li:visible');
        $visibleLangChoiceItems.each(function(idx, el){
            var urls = $('.download-setting', $(el)).filter('.is-hidden');
            if (urls.length){
                $('.status-error', $(el))
                    .text('Please upload the transcript file for this language or remove the language.')
            } else {
                isValid.push(1);
            }
        });
        if (isValid.length == $visibleLangChoiceItems.length) {
            fillValues(e);
        }
    };

    $('.save-button', element).bind('click', validateTranscripts);

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

    // End of Raccoongang changes

    // Raccoongang addons

    var transcriptsValue = [];
    var disabledLanguages = [];
    var $fileUploader = $('.input-file-uploader', element);
    var $defaultTranscriptUploader = $('.upload-default-transcript', element);
    var $defaultTranscriptRemover = $('.remove-default-transcript', element);
    var $langChoiceItem = $('.language-transcript-selector', element);
    var $videoApiAuthenticator = $('#video-api-authenticate', element);
    var gotTranscriptsValue = $('input[data-field-name="transcripts"]').val();
    var downloadTranscriptHandlerUrl = runtime.handlerUrl(element, 'download_transcript');
    var authenticateVideoApiHandlerUrl = runtime.handlerUrl(element, 'authenticate_video_api_handler');
    var uploadDefaultTranscriptHandlerUrl = runtime.handlerUrl(element, 'upload_default_transcript_handler');
    var currentLanguageCode;
    var currentLanguageLabel;

    /** Store all the default transcripts, fetched at document load, and their languages' codes. */
    var initialDefaultTranscripts = (function() {
        var defaultSubs = $('.initial-default-transcript');
        var initialDefaultTranscripts = [];
        defaultSubs.each(function(){
            var langCode = $(this).attr('data-lang-code');
            var langLabel = $(this).attr('data-lang-label');
            var downloadUrl = $(this).attr('data-download-url');
            var newSub = {'lang': langCode, 'label' : langLabel, 'url': downloadUrl};
            initialDefaultTranscripts.push(newSub);
        });
        return initialDefaultTranscripts;
    })();

    if (gotTranscriptsValue){
        transcriptsValue = JSON.parse(gotTranscriptsValue);
    }

    transcriptsValue.forEach(function(transcriptValue) {
        disabledLanguages.push(transcriptValue.lang)
    });

    function showStatus(message, type, successSelector, errorSelector){
        // Only one success message is to be displayed at once
        $('.api-request').empty();
        if(type==='success'){
            $(errorSelector).empty();
            $(successSelector).text(message).show();
            setTimeout(function(){
                $(successSelector).hide()
            }, 5000);
        }
        else if(type==='error'){
            $(successSelector).empty();
            $(errorSelector).text(message).show();
            setTimeout(function(){
                $(errorSelector).hide()
            }, 5000);
        }
    };

    /** Authenticate to video platform's API and show result message. */
    function authenticateVideoApi(data) {
        $.ajax({
            type: "POST",
            url: authenticateVideoApiHandlerUrl,
            data: JSON.stringify(data),
            dataType: 'json',
            success: function(response) {
                var error_message = response['error_message'];
                var success_message = response['success_message'];
                if(success_message) {
                    showStatus(
                        success_message,
                        'success',
                        '.api-request.authenticate.status-success',
                        '.api-request.authenticate.status-error');
                    showBackendSettings();
                }
                else if(error_message) {
                    showStatus(
                        error_message,
                        'error',
                        '.api-request.authenticate.status-success',
                        '.api-request.authenticate.status-error');
                }
            }
        })
        .fail(function(jqXHR) {
            var message = gettext('This may be happening because of an error with our server or your ' +
                'internet connection. Try refreshing the page or making sure you are online.');
            showStatus(
                message,
                'error',
                '.api-request.authenticate.status-success',
                '.api-request.authenticate.status-error'
            );
            if (jqXHR.responseText) { // Is there a more specific error message we can show?
                try {
                    message = JSON.parse(jqXHR.responseText).error;
                    if (typeof message === 'object' && message.messages) {
                        // e.g. {"error": {"messages": [{"text": "Unknown user 'bob'!", "type": "error"}, ...]}} etc.
                        message = $.map(message.messages, function(msg) { return msg.text; }).join(", ");
                        showStatus(
                            message,
                            'error',
                            '.api-request.authenticate.status-success',
                            '.api-request.authenticate.status-error'
                        );                   }
                } catch (error) {
                    message = jqXHR.responseText.substr(0, 300);
                    showStatus(
                        message,
                        'error',
                        '.api-request.authenticate.status-success',
                        '.api-request.authenticate.status-error'
                    );
                }
            }
            runtime.notify('error', {title: gettext('Unable to update settings'), message: message});
        });
    }

    function disableOption(){

        $langChoiceItem.find('option').each(function(ind){
            if (disabledLanguages.indexOf($(this).val()) > -1){
                $(this).attr('disabled', true)
            } else {
                $(this).attr('disabled', false)
            }
        })
    }
    /**
     * Replaces an existing transcript to transcriptsValue or adds new
     * Returns true if new one was added or false otherwise
     * @param {String} lang
     * @param {String} label
     * @param {String} url
     * @param {String} oldLang
     */
    function pushTranscript(lang, label, url, oldLang){
        var indexLanguage;
        for (var i=0; i < transcriptsValue.length; i++) {
            if (oldLang == transcriptsValue[i].lang || lang == transcriptsValue[i].lang) {
                indexLanguage = i;
                break;
            }
        }
        if (indexLanguage !== undefined) {
            transcriptsValue[indexLanguage].lang = lang;
            transcriptsValue[indexLanguage].label = label;
            if (url) {
              transcriptsValue[indexLanguage].url = url;
            }
            return false;
        } else {
            transcriptsValue.push({
                lang: lang,
                url: url,
                label: label
            });
            return true;
        }
    };

    function clickUploader(event) {
        event.preventDefault();
        event.stopPropagation();
        var $buttonBlock = $(event.currentTarget);
        var indexOfParentLi = $('.language-transcript-selector').children().index($buttonBlock.closest('li'));
        var langCode = $buttonBlock.attr('data-lang-code');
        var langLabel = $buttonBlock.attr('data-lang-label');
        var fieldNameDetails = $buttonBlock.attr('data-change-field-name') == 'transcripts' ? '.srt, .vtt' : '';
        var fieldName = $buttonBlock.attr('data-change-field-name');
        var dataLiIndex = $buttonBlock.attr('data-change-field-name') == 'transcripts' ? indexOfParentLi : '';
        $fileUploader.attr({
            'data-lang-code': langCode,
            'data-lang-label': langLabel,
            'data-change-field-name': fieldName,
            'accept': fieldNameDetails,
            'data-li-index': dataLiIndex
        });
        $fileUploader.click();
    };

    /** Upload a transcript available on a video platform to video xblock and update displayed default transcripts. */
    function uploadDefaultTranscriptsToServer(data) {
        $.ajax({
            type: "POST",
            url: uploadDefaultTranscriptHandlerUrl,
            data: JSON.stringify(data),
            dataType: 'json',
            success: function(response) {
                var newLang = response['lang'];
                var newLabel = response['label'];
                var newUrl = response['url'];
                pushTranscript(newLang, newLabel, newUrl, '');
                pushTranscriptsValue();
                // Add a transcript to the list of enabled ones
                var downloadUrl = downloadTranscriptHandlerUrl + '?' + newUrl;
                var defaultTranscript= {'lang': newLang, 'label': newLabel, 'url': downloadUrl};
                updateEnabledTranscriptBlockCreation(defaultTranscript);
                // Display status messages
                // var error_message = response['error_message'];
                var success_message = response['success_message'];
                if(success_message) {
                    showStatus(
                        success_message,
                        'success',
                        '.api-request.upload-default-transcript.' + newLang + '.status-success',
                        '.api-request.upload-default-transcript.' + newLang + '.status-error');
                }
            }
        })
        .fail(function(jqXHR) {
            var message = gettext('This may be happening because of an error with our server or your ' +
                'internet connection. Try refreshing the page or making sure you are online.');
            showStatus(
                message,
                'error',
                '.api-request.upload-default-transcript.' + currentLanguageCode + '.status-success',
                '.api-request.upload-default-transcript.' + currentLanguageCode + '.status-error'
            );
            if (jqXHR.responseText) { // Is there a more specific error message we can show?
                try {
                    message = JSON.parse(jqXHR.responseText).error;
                    if (typeof message === 'object' && message.messages) {
                        // e.g. {"error": {"messages": [{"text": "Unknown user 'bob'!", "type": "error"}, ...]}} etc.
                        message = $.map(message.messages, function(msg) { return msg.text; }).join(", ");
                        showStatus(
                            message,
                            'error',
                            '.api-request.upload-default-transcript.' + currentLanguageCode + '.status-success',
                            '.api-request.upload-default-transcript.' + currentLanguageCode + '.status-error'
                        );                   }
                } catch (error) {
                    message = jqXHR.responseText.substr(0, 300);
                    showStatus(
                        message,
                        'error',
                        '.api-request.upload-default-transcript.' + currentLanguageCode + '.status-success',
                        '.api-request.upload-default-transcript.' + currentLanguageCode + '.status-error'
                    );
                }
            }
            runtime.notify('error', {title: gettext('Unable to update settings'), message: message});
        });
    }

    function languageChecker(event) {
        event.stopPropagation();
        var $selectedOption = $(event.currentTarget).find('option:selected');
        var selectedLanguage = $selectedOption.val();
        var languageLabel = $selectedOption.attr('data-lang-label');
        var $langSelectParent = $(event.currentTarget).parent('li');
        var $uploadButton = $('.upload-transcript', $langSelectParent);
        var oldLang = $uploadButton.data('lang-code');
        if (selectedLanguage != oldLang && selectedLanguage != ''){
            var newTranscriptAdded = pushTranscript(selectedLanguage, languageLabel, undefined, oldLang);
            if (newTranscriptAdded){
                $uploadButton.removeClass('is-hidden');
            };
            $('.add-transcript').removeClass('is-disabled');
            disabledLanguages.push(selectedLanguage);
            if (oldLang != '') {
                removeLanguage(oldLang);
            }
            $uploadButton.data('lang-code', selectedLanguage);
        } else if (selectedLanguage == '') {
            $selectedOption.val($uploadButton.data('lang-code'));
            $('.remove-action', $langSelectParent).trigger('click');
        }
        $uploadButton.attr({
            'data-lang-code': selectedLanguage,
            'data-lang-label': languageLabel
        });
        disableOption();
        pushTranscriptsValue();
    }

    function removeLanguage(language) {
        var index = disabledLanguages.indexOf(language);
        disabledLanguages.splice(index, 1);
    }

    function removeTranscript(lang) {
        for (var i=0; i < transcriptsValue.length; i++) {
            if (lang == transcriptsValue[i].lang) {
                transcriptsValue.splice(i,1);
                break;
            }
        }
    }

    function pushTranscriptsValue() {
        transcriptsValue.forEach(function (transcriptValue, index, array) {
            if (transcriptValue.lang == '' || transcriptValue.label == '' || transcriptValue.url == '') {
                transcriptsValue.splice(index, 1);
            }
        });
        $('input[data-field-name="transcripts"]').val(JSON.stringify(transcriptsValue)).change();
    }

    function removeTranscriptBlock(event) {
        event.preventDefault();
        event.stopPropagation();
        var $currentBlock = $(event.currentTarget).closest('li');
        var lang = $currentBlock.find('option:selected').val();
        var label = $currentBlock.find('option:selected').attr('data-lang-label');
        removeTranscript(lang);
        if (!transcriptsValue.length) {
            $currentBlock.parents('li').removeClass('is-set').find('.setting-clear').removeClass('active').addClass('inactive');
        }
        removeLanguage(lang);
        pushTranscriptsValue();
        $currentBlock.remove();
        disableOption();
        // Affect default transcripts
        var enabledTranscript = {'lang' : lang, 'label' : label, 'url': ''};
        updateEnabledTranscriptBlockRemoval(enabledTranscript);
    }

   /** Get url of a specific transcript from a given transcripts array. */
   function getTranscriptUrl(transcriptsArray, langCode){
        var url = '';
        transcriptsArray.forEach(function(sub){
            if(sub['lang']==langCode){
              url = sub['url'];
            }
        });
        return url;
   }

    /** Create a new standard transcript block and fill it in automatically with transcript's data. */
    function createTranscriptBlock(langCode, langLabel) {
        // Create a transcript block if not already displayed
        $('.add-transcript').trigger('click');
        // Select language option
        var $createdOption = $('li.list-settings-item:visible select').last();
        $createdOption.val(langCode);
        var $createdLi = $('li.list-settings-item:visible').last();
        // Update language label
        $createdLi.val(langLabel);
        var $createdUploadReplace = $createdLi.find('a.upload-setting.upload-transcript:hidden');
        $createdUploadReplace.removeClass('is-hidden').html('Replace');
        var $createdDownload = $createdLi.find('a.download-transcript.download-setting:hidden');
        $createdDownload.removeClass('is-hidden');
        // Assign external download link
        var externalResourceUrl = getTranscriptUrl(transcriptsValue, langCode);
        var externalDownloadUrl = downloadTranscriptHandlerUrl + '?' + externalResourceUrl;
        $createdDownload.attr('href', externalDownloadUrl);
        $('.add-transcript', element).removeClass('is-disabled');
    }

    /** Affect standard transcripts on enabled sub creation and update a newly created enabled transcript. */
    function updateEnabledTranscriptBlockCreation(defaultTranscript){
        var langCode = defaultTranscript['lang'];
        var langLabel = defaultTranscript['label'];
        var downloadUrlServer = defaultTranscript['url']; // External url to download a resource from a server
        // Create new "standard" transcript block if it is not already in a displayed list
        var isNotDisplayedTranscript =
            $(".list-settings-item .list-settings-buttons .upload-setting:visible[data-lang-code=" + langCode + "]").length == 0;
        if (isNotDisplayedTranscript) { createTranscriptBlock(langCode, langLabel); }
        // Update attributes
        // Get external url from a newly created standard transcript
        if (!downloadUrlServer) {
            downloadUrlServer = $(".list-settings-buttons .upload-setting.upload-transcript[data-lang-code=" + langCode + "]")
                .siblings('a.download-transcript.download-setting').attr('href');
        }
        var $insertedEnabledTranscriptBlock = $('.enabled-default-transcripts-section .default-transcripts-label:visible').last();
        $insertedEnabledTranscriptBlock.attr('value', langCode).text(langLabel);
        var $downloadElement = $(".default-transcripts-action-link.download-transcript.download-setting:visible").last();
        $downloadElement.attr(
            {'data-lang-code': langCode, 'data-lang-label': langLabel, 'href': downloadUrlServer}
        );
        // Bind removal listener to a newly created enabled transcript
        var $removeElement = $(".default-transcripts-action-link.remove-default-transcript:visible").last();
        $removeElement
            .click(function() {
                var enabledTranscript = {'lang' : langCode, 'label' : langLabel, 'url': downloadUrlServer};
                updateEnabledTranscriptBlockRemoval(enabledTranscript);
            });
    }

    /** Update default transcripts on removal of an enabled transcript of choice. */
    function updateEnabledTranscriptBlockRemoval(enabledTranscript) {
        var langCode = enabledTranscript['lang'];
        var langLabel = enabledTranscript['label'];
        // Remove a standard transcript (xblock field Upload Transcript)
        var $transcriptBlock = $("a[data-lang-code='" + langCode + "']").closest("li.list-settings-item");
        removeTranscript(langCode);
        if (!transcriptsValue.length) {
            $transcriptBlock.parents('li').removeClass('is-set').find('.setting-clear').removeClass('active').addClass('inactive');
        }
        removeLanguage(langCode);
        pushTranscriptsValue();
        $('.add-transcript', element).removeClass('is-disabled');
        $transcriptBlock.remove();
        disableOption();
        // Get url for a transcript fetching from the API
        var downloadUrlApi = getTranscriptUrl(initialDefaultTranscripts, langCode); // External url for API call
        // Bind upload listener to a newly created available transcript
        $('.default-transcripts-action-link.upload-default-transcript').last()
            .click(function () {
                var data = {'lang': langCode, 'label': langLabel, 'url': downloadUrlApi};
                uploadDefaultTranscriptsToServer(data);
            });
    }

    function showUploadStatus($element, filename) {
        $('.status-error', $element).empty();
        $('.status-upload', $element).text('File ' + '"' + filename + '"' + ' uploaded successfully').show();
        setTimeout(function() {
            $('.status-upload', $element).hide();
        }, 5000);
    }

    function successHandler(response, statusText, xhr, fieldName, lang, label, currentLiTag) {
        var url = '/' + response['asset']['id'];
        var regExp = /.*@(.+\..+)/;
        var filename = regExp.exec(url)[1];
        var downloadUrl = downloadTranscriptHandlerUrl + '?' + url;
        if (fieldName == 'handout') {
            var $parentDiv = $('.file-uploader', element);
            $('.download-setting', $parentDiv).attr('href', downloadUrl).removeClass('is-hidden');
            $('a[data-change-field-name=' + fieldName + ']').text('Replace');
            showUploadStatus($parentDiv, filename);
            $('input[data-field-name=' + fieldName + ']').val(url).change();
        } else {
            pushTranscript(lang, label, url, '');
            $('.add-transcript').removeClass('is-disabled');
            $('input[data-field-name=' + fieldName + ']').val(JSON.stringify(transcriptsValue)).change();
            $(currentLiTag).find('.upload-transcript').text('Replace');
            $(currentLiTag).find('.download-transcript')
                .removeClass('is-hidden')
                .attr('href', downloadUrl);
            showUploadStatus($(currentLiTag), filename);
            // Update default transcripts with a new enabled transcript if all the data were provided.
            if (label) {
                var defaultTranscript = {'lang': lang, 'label': label, 'url': downloadUrl};
                updateEnabledTranscriptBlockCreation(defaultTranscript);
            }
        }
        $(event.currentTarget).attr({
            'data-change-field-name': '',
            'data-lang-code': '',
            'data-lang-label': ''
        });
    };

    $videoApiAuthenticator.on('click', function(event) {
        event.preventDefault();
        event.stopPropagation();
        var $data = $('.token', element).val();
        authenticateVideoApi($data);
    });

    $fileUploader.on('change', function(event) {
        if (!$fileUploader.val()) {
            return;
        }
        var fieldName = $(event.currentTarget).attr('data-change-field-name');
        var lang = $(event.currentTarget).attr('data-lang-code');
        var label = $(event.currentTarget).attr('data-lang-label');
        var currentLiIndex = $(event.currentTarget).attr('data-li-index');
        var currentLiTag = $('.language-transcript-selector').children()[parseInt(currentLiIndex)];
        $('.upload-setting', element).addClass('is-disabled');
        $('.file-uploader-form', element).ajaxSubmit({
            success: function(response, statusText, xhr) {
                successHandler(response, statusText, xhr, fieldName, lang, label, currentLiTag)
            },
            error: function(jqXHR, textStatus, errorThrown) {
                runtime.notify('error', {title: gettext('Unable to update settings'), message: textStatus});
            }
        });
        $('.upload-setting', element).removeClass('is-disabled');
    });

    $('.add-transcript', element).on('click', function (event) {
        var $templateItem = $('.list-settings-item:hidden').clone();
        event.preventDefault();
        $(event.currentTarget).addClass('is-disabled');
        $templateItem.removeClass('is-hidden').appendTo($langChoiceItem);
        $('.upload-transcript', $templateItem).on('click', clickUploader);
        $('.lang-select', $templateItem).on('change', languageChecker);
        $('.remove-action', element).on('click', removeTranscriptBlock);
    });

    $('.lang-select').on('change', languageChecker);

    $('.upload-transcript, .upload-action', element).on('click', clickUploader);

    $defaultTranscriptUploader.click(function(event) {
        event.preventDefault();
        event.stopPropagation();
        var langCode = $(event.currentTarget).attr('data-lang-code');
        var label = $(event.currentTarget).attr('data-lang-label');
        var url = $(event.currentTarget).attr('data-download-url');
        currentLanguageCode = langCode;
        currentLanguageLabel = label;
        var data = {'lang': langCode, 'label' : label, 'url' : url};
        uploadDefaultTranscriptsToServer(data);
    });

    $('.remove-action', element).on('click', removeTranscriptBlock);

    $defaultTranscriptRemover.click(function(){
        var langCode = $(event.currentTarget).attr('data-lang-code');
        var langLabel = $(event.currentTarget).attr('data-lang-label');
        var downloadUrl = $(event.currentTarget).attr('data-download-url');
        var enabledTranscript = {'lang' : langCode, 'label' : langLabel, 'url': downloadUrl};
        updateEnabledTranscriptBlockRemoval(enabledTranscript);
    });

    $('.setting-clear').on('click', function (event) {
        var $currentBlock = $(event.currentTarget).closest('li');
        if ($('.file-uploader', $currentBlock).length > 0) {
            $('.upload-setting', $currentBlock).text('Upload');
            $('.download-setting', $currentBlock).addClass('is-hidden');
        }
        $currentBlock.find('ol').find('li:visible').remove();
    });
    $().ready(function() {
        disableOption();
    });

    function parseRelativeTime(value) {
        // This function ensure you have two-digits
        // By default max value of RelativeTime field on Backend is 23:59:59,
        // that is 86399 seconds.
        var maxTimeInSeconds = 86399;
        var pad = function (number) {
                return (number < 10) ? '0' + number : number;
            };
        // Removes all white-spaces and splits by `:`.
        var list = value.replace(/\s+/g, '').split(':');
        var seconds;
        var date;

        list = _.map(list, function (num) {
            return Math.max(0, parseInt(num, 10) || 0);
        }).reverse();

        seconds = _.reduce(list, function (memo, num, index) {
            return memo + num * Math.pow(60, index);
        }, 0);

        // multiply by 1000 because Date() requires milliseconds
        date = new Date(Math.min(seconds, maxTimeInSeconds) * 1000);

        return [
            pad(date.getUTCHours()),
            pad(date.getUTCMinutes()),
            pad(date.getUTCSeconds())
        ].join(':');
    };
    // End of Raccoongang addons
}
