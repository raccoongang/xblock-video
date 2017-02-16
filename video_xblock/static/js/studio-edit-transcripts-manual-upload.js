/**
 * Standard transcripts (manually uploaded) functionality is represented here.
 */

/**
 * Display message with results on a transcript manual upload.
 */
function showUploadStatus($element, filename) {
    'use strict';

    $('.status-error', $element).empty();
    $('.status-upload', $element).text('File ' + '"' + filename + '"' + ' uploaded successfully').show();
    setTimeout(function() {
        $('.status-upload', $element).hide();
    }, 5000);
}

/**
 * Ensure transcript text's timing has two-digits.
 * By default max value of RelativeTime field on Backend is 23:59:59, that is 86399 seconds.
 */
function parseRelativeTime(value) {
    'use strict';

    var maxTimeInSeconds = 86399;
    var pad = function (number) {
            return (number < 10) ? '0' + number : number;
        };
    // Remove all white-spaces and splits by `:`.
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
}

/**
 * Validate transcript data before to save it to video xblock.
 */
function validateTranscripts(e, $langChoiceItem) {
    'use strict';

    e.preventDefault();
    var isValid = [];
    var $visibleLangChoiceItems = $langChoiceItem.find('li:visible');
    $visibleLangChoiceItems.each(function(idx, el) {
        var urls = $('.download-setting', $(el)).filter('.is-hidden');
        if (urls.length) {
            $('.status-error', $(el))
                .text('Please upload the transcript file for this language or remove the language.')
        } else {
            isValid.push(1);
        }
    });
    return isValid.length == $visibleLangChoiceItems.length;
}

/**
 * Replace an existing transcript to transcriptsValue or adds new
 * Return true if new one was added or false otherwise
 * @param {String} lang
 * @param {String} label
 * @param {String} url
 * @param {String} oldLang
 * @param {Array} transcriptsValue
 */
function pushTranscript(lang, label, url, oldLang, transcriptsValue) {
    'use strict';

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
}

function removeLanguage(language, disabledLanguages) {
    'use strict';

    var index = disabledLanguages.indexOf(language);
    disabledLanguages.splice(index, 1);
}

function removeTranscript(lang, transcriptsValue) {
    'use strict';

    for (var i=0; i < transcriptsValue.length; i++) {
        if (lang == transcriptsValue[i].lang) {
            transcriptsValue.splice(i,1);
            break;
        }
    }
}

/**
 * Disable language option already selected when uploading a transcript.
 */
function disableOption($langChoiceItem, disabledLanguages) {
    'use strict';

    $langChoiceItem.find('option').each(function(ind) {
        if (disabledLanguages.indexOf($(this).val()) > -1) {
            $(this).attr('disabled', true)
        } else {
            $(this).attr('disabled', false)
        }
    })
}

function pushTranscriptsValue(transcriptsValue) {
    'use strict';

    transcriptsValue.forEach(function (transcriptValue, index, array) {
        if (transcriptValue.lang == '' || transcriptValue.label == '' || transcriptValue.url == '') {
            transcriptsValue.splice(index, 1);
        }
    });
    $('input[data-field-name="transcripts"]').val(JSON.stringify(transcriptsValue)).change();
}

/**
 * Create a new standard transcript block and fill it in automatically with transcript's data.
 */
function createTranscriptBlock(langCode, langLabel, transcriptsValue, downloadTranscriptHandlerUrl) {
    'use strict';
    // Create a transcript block if not already displayed
    $('.add-transcript').trigger('click');
    // Select language option
    var $createdOption = $('li.list-settings-item:visible select').last();
    $createdOption.val(langCode);
    var $createdLi = $('li.list-settings-item:visible').last();
    // Update language label
    $createdLi.val(langLabel);
    var $createdUploadReplace = $createdLi.find('a.upload-setting.upload-transcript:hidden');
    $createdUploadReplace
        .removeClass('is-hidden')
        .html('Replace')
        .attr({'data-lang-code': langCode, 'data-lang-label': langLabel});
    var $createdDownload = $createdLi.find('a.download-transcript.download-setting:hidden');
    $createdDownload.removeClass('is-hidden');
    // Assign external download link
    var externalResourceUrl = getTranscriptUrl(transcriptsValue, langCode);
    var externalDownloadUrl = downloadTranscriptHandlerUrl + '?' + externalResourceUrl;
    $createdDownload.attr('href', externalDownloadUrl);
    $('.add-transcript').removeClass('is-disabled');
}

function clickUploader(event, $fileUploader) {
    'use strict';
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
}

/**
 * Check for language of a transcript being manually uploaded.
 */
function languageChecker(event, transcriptsValue, disabledLanguages) {
    'use strict';
    event.stopPropagation();
    var $selectedOption = $(event.currentTarget).find('option:selected');
    var selectedLanguage = $selectedOption.val();
    var languageLabel = $selectedOption.attr('data-lang-label');
    var $langSelectParent = $(event.currentTarget).parent('li');
    var $uploadButton = $('.upload-transcript', $langSelectParent);
    var oldLang = $uploadButton.data('lang-code');
    if (selectedLanguage != oldLang && selectedLanguage != '') {
        var newTranscriptAdded = pushTranscript(selectedLanguage, languageLabel, '', oldLang, transcriptsValue);
        if (newTranscriptAdded) {
            $uploadButton.removeClass('is-hidden');
        }
        $('.add-transcript').removeClass('is-disabled');
        disabledLanguages.push(selectedLanguage);
        if (oldLang != '') {
            removeLanguage(oldLang, disabledLanguages);
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
}

function disableTranscriptBlock(transcriptsValue, $currentBlock) {
    'use strict';
    if (!transcriptsValue.length) {
        $currentBlock.parents('li').removeClass('is-set').find('.setting-clear').removeClass('active').addClass('inactive');
    }
}

/**
 * Manually remove a transcript of choice. Used for standard transcripts functionality only.
 */
function removeTranscriptBlock(event, transcriptsValue, disabledLanguages) {
    'use strict';
    event.preventDefault();
    event.stopPropagation();
    var $currentBlock = $(event.currentTarget).closest('li');
    var lang = $currentBlock.find('option:selected').val();
    var label = $currentBlock.find('option:selected').attr('data-lang-label');
    removeTranscript(lang, transcriptsValue);
    disableTranscriptBlock(transcriptsValue, $currentBlock);
    removeLanguage(lang, disabledLanguages);
    pushTranscriptsValue(transcriptsValue);
    $currentBlock.remove();
}

/**
 * Automatically remove standard transcript. Used with default transcripts functionality.
 */
function removeStandardTranscriptBlock(langCode, transcriptsValue, disabledLanguages) {
    'use strict';
    var $transcriptBlock = $('a[data-lang-code=' + langCode + ']').closest('li.list-settings-item');
    removeTranscript(langCode, transcriptsValue);
    disableTranscriptBlock(transcriptsValue, $transcriptBlock);
    removeLanguage(langCode, disabledLanguages);
    pushTranscriptsValue(transcriptsValue);
    $('.add-transcript').removeClass('is-disabled');
    $transcriptBlock.remove();
}
