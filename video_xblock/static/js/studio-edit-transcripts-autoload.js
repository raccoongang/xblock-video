/**
 * Default transcripts functionality is represented here.
 */

/**
 * Get url of a specific transcript from a given transcripts array.
 */
function getTranscriptUrl(transcriptsArray, langCode){
    var url = '';
    transcriptsArray.forEach(function(sub){
        if(sub['lang']==langCode){
          url = sub['url'];
        }
    });
    return url;
}

/**
 * Create elements to display messages with status on actions with default transcripts.
 */
function createStatusMessageElement(langCode, actionSelector){
    var errorMessageElementParentSelector = '';
    var successMessageElementParentSelector = '';
    if (actionSelector === 'upload-default-transcript') {
        errorMessageElementParentSelector = 'available-default-transcripts-section';
        successMessageElementParentSelector = 'enabled-default-transcripts-section';
    }
    else if (actionSelector === 'remove-default-transcript') {
        errorMessageElementParentSelector = 'enabled-default-transcripts-section';
        successMessageElementParentSelector = 'available-default-transcripts-section';
    }
    var isNotDisplayedErrorMessageElement = $(".api-request." + actionSelector + "." + langCode + ".status-error").length == 0;
    var isNotDisplayedSuccessMessageElement = $(".api-request." + actionSelector + "." + langCode + ".status-success").length == 0;
    if (isNotDisplayedErrorMessageElement && isNotDisplayedSuccessMessageElement)
    {
        var $errorMessageUpload = $("<div>", {"class": "api-request " + actionSelector + " " + langCode + " status-error"});
        $errorMessageUpload.appendTo($('.' + errorMessageElementParentSelector + ':visible').last());
        var $successMessageUpload = $("<div>", {"class": "api-request " + actionSelector + " " + langCode + " status-success"});
        $successMessageUpload.appendTo($('.' + successMessageElementParentSelector + ':visible').last());
    }
}

/**
 * Display message with results on a performed action.
 */
function showStatus(message, type, successSelector, errorSelector){
    // Only one success message is to be displayed at once
    $('.api-request').empty();
    var selectorToEmpty = '';
    var selectorToShow = '';
    if(type==='success'){
        selectorToEmpty = errorSelector;
        selectorToShow = successSelector;
    }
    else if(type==='error'){
        selectorToEmpty = successSelector;
        selectorToShow = errorSelector;
    }
    $(selectorToEmpty).empty();
    $(selectorToShow).text(message).show();
    setTimeout(function(){
        $(errorSelector).hide()
    }, 5000);
}

/**
 *  Store all the default transcripts, fetched at document load, and their languages' codes.
 */
function getInitialDefaultTranscriptsData() {
        var defaultSubs = $('.initial-default-transcript');
        var initialDefaultTranscripts = [];
        var langCodes = [];
        defaultSubs.each(function(){
            var langCode = $(this).attr('data-lang-code');
            var langLabel = $(this).attr('data-lang-label');
            var downloadUrl = $(this).attr('data-download-url');
            var newSub = {'lang': langCode, 'label' : langLabel, 'url': downloadUrl};
            initialDefaultTranscripts.push(newSub);
            langCodes.push(langCode);
        });
        return [initialDefaultTranscripts, langCodes];
}

function getDefaultTranscriptsArray(defaultTranscriptType){
    var defaultTranscriptsArray = [];
    $('.' + defaultTranscriptType + '-default-transcripts-section .default-transcripts-label:visible').each(function(){
        var code = $(this).attr('value');
        defaultTranscriptsArray.push(code);
    });
    return defaultTranscriptsArray;
}

/** Create available transcript. */
function createAvailableTranscriptBlock(defaultTranscript, initialDefaultTranscriptsData){
    var langCode = defaultTranscript['lang'];
    var langLabel = defaultTranscript['label'];
    var initialDefaultTranscripts = initialDefaultTranscriptsData[0];
    var initialDefaultTranscriptsLangCodes = initialDefaultTranscriptsData[1];
    // Get all the currently available transcripts
    var allAvailableTranscripts = getDefaultTranscriptsArray('available');
    // Create a new available transcript if stored on a platform and doesn't already exist on video xblock
    var isNotDisplayedAvailableTranscript = $.inArray(langCode, allAvailableTranscripts) == -1;
    var isStoredVideoPlatform = $.inArray(langCode, initialDefaultTranscriptsLangCodes) !== -1;
    if (isNotDisplayedAvailableTranscript && isStoredVideoPlatform) {
        // Show label of available transcripts if no such label is displayed
        var $availableLabel = $("div.custom-field-section-label:contains('Available transcripts')");
        var isHiddenAvailableLabel = !$("div.custom-field-section-label:contains('Available transcripts'):visible").length;
        if (isHiddenAvailableLabel) { $availableLabel.removeClass('is-hidden'); }
        // Create a default (available) transcript block
        var $newAvailableTranscriptBlock = $('.available-default-transcripts-section:hidden').clone();
        $newAvailableTranscriptBlock.removeClass('is-hidden').appendTo($('.default-transcripts-wrapper'));
        $('.default-transcripts-label:visible').last().attr('value', langCode).text(langLabel);
        // Get url for a transcript fetching from the API
        var downloadUrlApi = getTranscriptUrl(initialDefaultTranscripts, langCode); // External url for API call
        // Update attributes
        $('.default-transcripts-action-link.upload-default-transcript').last()
            .attr({'data-lang-code': langCode, 'data-lang-label': langLabel, 'data-download-url': downloadUrlApi})
        // Create elements to display status messages on available transcript upload
        createStatusMessageElement(langCode, 'upload-default-transcript');
    }
}

/** Display a transcript in a list of enabled transcripts. Listeners on removal are bound in studio editor js.*/
function createEnabledTranscriptBlock(defaultTranscript, downloadUrlServer){
    var langCode = defaultTranscript['lang'];
    var langLabel = defaultTranscript['label'];
    // var downloadUrlServer = defaultTranscript['url']; // TODO add to docstring::: External url to download a resource from a server
    var $availableTranscriptBlock = $("div[value='" + langCode + "']")
        .closest("div.available-default-transcripts-section:visible");
    // Remove a transcript of choice from the list of available ones
    $availableTranscriptBlock.remove();
    // Hide label of available transcripts if no such items left
    if (!$("div.available-default-transcripts-section:visible").length) {
        $("div.custom-field-section-label:contains('Available transcripts')").addClass('is-hidden');
    }
    // Get all the currently enabled transcripts
    var allEnabledTranscripts = getDefaultTranscriptsArray('enabled');
    // Create a new enabled transcript if it doesn't already exist in a video xblock
    var isNotDisplayedEnabledTranscript = $.inArray(langCode, allEnabledTranscripts) == -1;
    if (isNotDisplayedEnabledTranscript) {
        // Display label of enabled transcripts if hidden
        var $enabledLabel = $("div.custom-field-section-label:contains('Enabled transcripts')");
        var isHiddenEnabledLabel = !$("div.custom-field-section-label:contains('Enabled transcripts'):visible").length;
        if (isHiddenEnabledLabel) { $enabledLabel.removeClass('is-hidden'); }
        // Create a default (enabled) transcript block
        var $newEnabledTranscriptBlock = $('.enabled-default-transcripts-section:hidden').clone();
        // Insert a new default transcript block
        var $lastEnabledTranscriptBlock = $('.enabled-default-transcripts-section:visible').last();
        var $parentElement = (isHiddenEnabledLabel) ? $enabledLabel : $lastEnabledTranscriptBlock;
        $newEnabledTranscriptBlock.removeClass('is-hidden').insertAfter($parentElement);
        // Update attributes
        var $insertedEnabledTranscriptBlock = $('.enabled-default-transcripts-section .default-transcripts-label:visible').last();
        $insertedEnabledTranscriptBlock.attr('value', langCode).text(langLabel);
        var $downloadElement = $(".default-transcripts-action-link.download-transcript.download-setting:visible").last();
        $downloadElement.attr(
            {'data-lang-code': langCode, 'data-lang-label': langLabel, 'href': downloadUrlServer}
        );
        var $removeElement = $(".default-transcripts-action-link.remove-default-transcript:visible").last();
        // $(".default-transcripts-action-link.remove-default-transcript:visible[data-lang-code=" + langCode + "]");
        $removeElement.attr({'data-lang-code': langCode, 'data-lang-label': langLabel});
    }
}

/** Remove enabled transcript of choice. */
function removeEnabledTranscriptBlock(enabledTranscript, initialDefaultTranscriptsData) {
    var langCode = enabledTranscript['lang'];
    var langLabel = enabledTranscript['label'];
    var initialDefaultTranscriptsLangCodes = initialDefaultTranscriptsData[1];
    // Remove enabled transcript of choice
    var $enabledTranscriptBlock = $("div[value='" + langCode + "']").closest("div.enabled-default-transcripts-section");
    $enabledTranscriptBlock.remove();
    // Hide label of enabled transcripts if no such items left
    if (!$("div.enabled-default-transcripts-section:visible").length) {
        $("div.custom-field-section-label:contains('Enabled transcripts')").addClass('is-hidden');
    }
    // Create elements to display status messages on enabled transcript removal
    createStatusMessageElement(langCode, 'remove-default-transcript');
    // Display message with results on removal
    // Get all the currently enabled transcripts
    var allEnabledTranscripts = getDefaultTranscriptsArray('enabled');
    var isSuccessfulRemoval = $.inArray(langCode, allEnabledTranscripts) == -1; // Is not in array
    var isStoredVideoPlatform = $.inArray(langCode, initialDefaultTranscriptsLangCodes) !== -1;  // Is in array
    var successMessageRemoval = langLabel + " transcripts are successfully removed from the list of enabled ones.";
    var errorMessage = langLabel + " transcripts are removed, but can not be uploaded from the video platform.";
    var failureMessage = langLabel + " transcripts are not neither removed nor added to the list of available ones.";
    if(isSuccessfulRemoval && isStoredVideoPlatform) {
        showStatus(
            successMessageRemoval,
            'success',
            '.api-request.remove-default-transcript.' + langCode + '.status-success',
            '.api-request.remove-default-transcript.' + langCode + '.status-error');
    }
    else if(isSuccessfulRemoval && !isStoredVideoPlatform){
        showStatus(
            errorMessage,
            'error',
            '.api-request.remove-default-transcript.' + langCode + '.status-success',
            '.api-request.remove-default-transcript.' + langCode + '.status-error');
    }
    else {
        showStatus(
            failureMessage,
            'error',
            '.api-request.remove-default-transcript.' + langCode + '.status-success',
            '.api-request.remove-default-transcript.' + langCode + '.status-error');
    }
}


