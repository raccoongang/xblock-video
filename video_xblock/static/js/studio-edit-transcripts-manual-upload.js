/**
 * Standard transcripts (manually uploaded ones) and captions functionality is represented here.
 * Transcripts and captions often share the same logic.
 */

/**
 * Display message with results on a performed action with captions.
 */
function displayStatusCaptions(statusType, statusMessage, $parentDiv) {
    'use strict';
    var $successElement = $('.status-upload', $parentDiv);
    var $errorElement = $('.status-error', $parentDiv);
    showStatus(
        statusMessage,
        statusType,
        $successElement,
        $errorElement);
}

/**
 * Display message with results on a performed action with transcripts.
 */
function displayStatusTranscripts(statusType, statusMessage, currentLiTag) {
    'use strict';
    var $successElement = $('.status-upload', $(currentLiTag));
    var $errorElement = $('.status-error', $(currentLiTag));
    showStatus(
        statusMessage,
        statusType,
        $successElement,
        $errorElement);
}

/**
 * Ensure transcript text's timing has two-digits.
 * By default max value of RelativeTime field on Backend is 23:59:59, that is 86399 seconds.
 */
function parseRelativeTime(value) {
    'use strict';
    var maxTimeInSeconds = 86399;
    var pad = function(number) {
        return (number < 10) ? '0' + number : number;
    };
    // Remove all white-spaces and splits by `:`.
    var list = value.replace(/\s+/g, '').split(':');
    var seconds;
    var date;

    list = $.map(list, function(num) {
        return Math.max(0, parseInt(num, 10) || 0);
    }).reverse();

    seconds = $.reduce(list, function(memo, num, index) {
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
 * Get url of a specific transcript from a given transcripts array.
 */
function getTranscriptUrl(transcriptsArray, langCode) {
    'use strict';
    var url = '';
    transcriptsArray.forEach(function(sub) {
        if (sub.lang === langCode) {
            url = sub.url;
        }
    });
    return url;
}

/**
 * Validate transcript data before save it to video xblock.
 */
function validateTranscripts(e, $langChoiceItem) {
    'use strict';
    var isValid = [];
    var $visibleLangChoiceItems = $langChoiceItem.find('li:visible');
    var urls;
    e.preventDefault();
    $visibleLangChoiceItems.each(function(idx, el) {
        urls = $('.download-setting', $(el)).filter('.is-hidden');
        if (urls.length) {
            $('.status-error', $(el))
                .text('Please upload the transcript file for this language or remove the language.');
        } else {
            isValid.push(1);
        }
    });
    return isValid.length === $visibleLangChoiceItems.length;
}

/**
 * Validate extension and name of a transcript or a caption file before save it to video xblock.
 *
 * Returns:
 * isValidated (Boolean): Result of a validation (true|false).
 *
 */
function validateTranscriptFile(event, fieldName, filename, $fileUploader) {
    'use strict';
    // User may upload a file without extension. Reference: http://stackoverflow.com/a/1203361
    var fileExtension = filename.substr((~-filename.lastIndexOf(".") >>> 0) + 2);
    var fileSize = $fileUploader[0].files[0].size;
    var acceptedFormats = $fileUploader[0].accept || '.vtt .srt';
    var isEmptyExtension = fileExtension === '';
    var isNotAcceptedExtension = acceptedFormats.indexOf(fileExtension) === -1;
    var isNotAcceptedFormat = isEmptyExtension || isNotAcceptedExtension;
    var isNotAcceptedSize = fileSize > 307200;
    var isNotAccepted = false;
    var errorMessage = 'Couldn\'t upload "' + filename + '". ';
    var $parentDiv;
    var currentLiIndex;
    var currentLiTag;
    var isValidated;
    // We still need to validate file extension, since a user can override an `accept` attribute,
    // that is, choose file of any format to submit through a file upload
    if (isNotAcceptedFormat) {
        errorMessage = errorMessage + 'Please upload a file of "vtt" or "srt" format only. ';
        isNotAccepted = true;
        console.log(errorMessage);
    }
    if (isNotAcceptedSize) {
        errorMessage = errorMessage + 'Please upload a file of 300 KB maximum.';
        isNotAccepted = true;
        console.log(errorMessage);
    }
    // Display validation error message if a transcript/caption file may not be not accepted
    if (isNotAccepted) {
        if (fieldName == 'handout') {
            $parentDiv = $('.file-uploader');
            displayStatusCaptions('error', errorMessage, $parentDiv)
        } else {
            currentLiIndex = $(event.currentTarget).attr('data-li-index');
            currentLiTag = $('.language-transcript-selector').children()[parseInt(currentLiIndex)];
            displayStatusTranscripts('error', errorMessage, currentLiTag)
        }
        isValidated = false;
    } else {
        isValidated = true;
    }

    return isValidated;
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
    var i;
    for (i = 0; i < transcriptsValue.length; i++) {
        if (oldLang === transcriptsValue[i].lang || lang === transcriptsValue[i].lang) {
            indexLanguage = i;
            break;
        }
    }
    if (indexLanguage !== undefined) {
        transcriptsValue[indexLanguage].lang = lang;  // eslint-disable-line no-param-reassign
        transcriptsValue[indexLanguage].label = label;  // eslint-disable-line no-param-reassign
        if (url) {
            transcriptsValue[indexLanguage].url = url;  // eslint-disable-line no-param-reassign
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

/**
 * Disable a specific language.
 */
function removeLanguage(language, disabledLanguages) {
    'use strict';
    var index = disabledLanguages.indexOf(language);
    disabledLanguages.splice(index, 1);
}

/**
 * Remove a transcript from a standard transcripts array.
 */
function removeTranscript(lang, transcriptsValue) {
    'use strict';
    var i;
    for (i = 0; i < transcriptsValue.length; i++) {
        if (lang === transcriptsValue[i].lang) {
            transcriptsValue.splice(i, 1);
            break;
        }
    }
}

/**
 * Disable language option already selected when uploading a transcript.
 */
function disableOption($langChoiceItem, disabledLanguages) {
    'use strict';
    $langChoiceItem.find('option').each(function() {
        if (disabledLanguages.indexOf($(this).val()) > -1) {
            $(this).attr('disabled', true);
        } else {
            $(this).attr('disabled', false);
        }
    });
}

/**
 * Add a new transcript to a standard transcripts array.
 */
function pushTranscriptsValue(transcriptsValue) {
    'use strict';
    transcriptsValue.forEach(function(transcriptValue, index) {
        if (transcriptValue.lang === '' || transcriptValue.label === '' || transcriptValue.url === '') {
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
    var $createdOption;
    var $createdLi;
    var $createdUploadReplace;
    var $createdDownload;
    var externalResourceUrl;
    var externalDownloadUrl;
    // Create a transcript block if not already displayed
    $('.add-transcript').trigger('click');
    // Select language option
    $createdOption = $('li.list-settings-item:visible select').last();
    $createdOption.val(langCode);
    $createdLi = $('li.list-settings-item:visible').last();
    // Update language label
    $createdLi.val(langLabel);
    $createdUploadReplace = $createdLi.find('a.upload-setting.upload-transcript:hidden');
    $createdUploadReplace
        .removeClass('is-hidden')
        .html('Replace')
        .attr({'data-lang-code': langCode, 'data-lang-label': langLabel});
    $createdDownload = $createdLi.find('a.download-transcript.download-setting:hidden');
    $createdDownload.removeClass('is-hidden');
    // Assign external download link to href attribute
    externalResourceUrl = getTranscriptUrl(transcriptsValue, langCode);
    externalDownloadUrl = downloadTranscriptHandlerUrl + '?' + externalResourceUrl;
    $createdDownload.attr('href', externalDownloadUrl);
    $('.add-transcript').removeClass('is-disabled');
}

/**
 * Assign transcript's data to file uploader's attributes.
 */
function clickUploader(event, $fileUploader) {
    'use strict';
    var $buttonBlock = $(event.currentTarget);
    var indexOfParentLi = $('.language-transcript-selector').children().index($buttonBlock.closest('li'));
    var langCode = $buttonBlock.attr('data-lang-code');
    var langLabel = $buttonBlock.attr('data-lang-label');
    var fieldNameDetails = $buttonBlock.attr('data-change-field-name') === 'transcripts' ? '.srt, .vtt' : '';
    var fieldName = $buttonBlock.attr('data-change-field-name');
    var dataLiIndex = $buttonBlock.attr('data-change-field-name') === 'transcripts' ? indexOfParentLi : '';
    event.preventDefault();
    event.stopPropagation();
    $fileUploader.attr({
        'data-lang-code': langCode,
        'data-lang-label': langLabel,
        'data-change-field-name': fieldName,
        'data-li-index': dataLiIndex,
        accept: fieldNameDetails
    });
    $fileUploader.click();
}

/**
 * Check for language of a transcript being manually uploaded.
 */
function languageChecker(event, transcriptsValue, disabledLanguages) {
    'use strict';
    var $selectedOption = $(event.currentTarget).find('option:selected');
    var selectedLanguage = $selectedOption.val();
    var languageLabel = $selectedOption.attr('data-lang-label');
    var $langSelectParent = $(event.currentTarget).parent('li');
    var $uploadButton = $('.upload-transcript', $langSelectParent);
    var oldLang = $uploadButton.data('lang-code');
    var newTranscriptAdded;
    event.stopPropagation();
    if (selectedLanguage !== oldLang && selectedLanguage !== '') {
        newTranscriptAdded = pushTranscript(selectedLanguage, languageLabel, '', oldLang, transcriptsValue);
        if (newTranscriptAdded) {
            $uploadButton.removeClass('is-hidden');
        }
        $('.add-transcript').removeClass('is-disabled');
        disabledLanguages.push(selectedLanguage);
        if (oldLang !== '') {
            removeLanguage(oldLang, disabledLanguages);
        }
        $uploadButton.data('lang-code', selectedLanguage);
    } else if (selectedLanguage === '') {
        $selectedOption.val($uploadButton.data('lang-code'));
        $('.remove-action', $langSelectParent).trigger('click');
    }
    $uploadButton.attr({
        'data-lang-code': selectedLanguage,
        'data-lang-label': languageLabel
    });
}

/**
 * Prevent transcripts block from being modified.
 */
function disableTranscriptBlock(transcriptsValue, $currentBlock) {
    'use strict';
    if (!transcriptsValue.length) {
        $currentBlock.parents('li').removeClass('is-set').find('.setting-clear')
            .removeClass('active')
            .addClass('inactive');
    }
}

/**
 * Manually remove a transcript of choice. Used for standard transcripts functionality only.
 */
function removeTranscriptBlock(event, transcriptsValue, disabledLanguages) {
    'use strict';
    var $currentBlock = $(event.currentTarget).closest('li');
    var lang = $currentBlock.find('option:selected').val();
    event.preventDefault();
    event.stopPropagation();
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
