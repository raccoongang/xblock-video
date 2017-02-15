/**
 * Default transcripts functionality is represented here.
 */

/** Run a callback when DOM is fully loaded */
var domReady = function(callback) {
    if (document.readyState === "interactive" || document.readyState === "complete") {
        callback();
    } else {
        document.addEventListener("DOMContentLoaded", callback);
    }
};

/** Get url of a specific transcript from a given transcripts array. */
var getTranscriptUrl = function(transcriptsArray, langCode){
    var url = '';
    transcriptsArray.forEach(function(sub){
        if(sub['lang']==langCode){
          url = sub['url'];
        }
    });
    return url;
};

/** Create elements to display messages with status on actions with default transcripts. */
var createStatusMessageElement = function(langCode, actionSelector){
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
};

/** Display message with results on a performed action. */
var showStatus = function(message, type, successSelector, errorSelector){
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

domReady(function() {
    'use strict';

    var $defaultTranscriptUploader = $('.upload-default-transcript');
    var $defaultTranscriptRemover = $('.remove-default-transcript');

    /** Store all the default transcripts, fetched at document load, and their languages' codes. */
    var initialDefaultTranscriptsData = (function() {
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
    })();
    var initialDefaultTranscripts = initialDefaultTranscriptsData[0];
    var initialDefaultTranscriptsLangCodes = initialDefaultTranscriptsData[1];

    /** Display a transcript in a list of enabled transcripts. Listeners on removal are bound in studio editor js.*/
    var createEnabledTranscriptBlock = function(defaultTranscript){
        var langCode = defaultTranscript['lang'];
        var langLabel = defaultTranscript['label'];
        var downloadUrlServer = defaultTranscript['url']; // External url to download a resource from a server
        // Get all the currently enabled transcripts
        var allEnabledTranscripts = [];
        $('.enabled-default-transcripts-section .default-transcripts-label:visible').each(function(){
            var code = $(this).attr('value');
            allEnabledTranscripts.push(code);
        });
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
            // Bind removal listener to a newly created enabled transcript
            var $removeElement = $(".default-transcripts-action-link.remove-default-transcript:visible").last();
            $removeElement
                .attr({'data-lang-code': langCode, 'data-lang-label': langLabel})
                .click(function() {
                    var enabledTranscript = {'lang' : langCode, 'label' : langLabel, 'url': downloadUrlServer};
                    removeEnabledTranscriptBlock(enabledTranscript);
                });
        }
    };

    /** Create available transcript. */
    var createAvailableTranscriptBlock = function(defaultTranscript){
        var langCode = defaultTranscript['lang'];
        var langLabel = defaultTranscript['label'];
        // Get all the currently available transcripts
        var allAvailableTranscripts = [];
        $('.available-default-transcripts-section .default-transcripts-label:visible').each(function(){
            var code = $(this).attr('value');
            allAvailableTranscripts.push(code);
        });
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
    };

    /** Remove enabled transcript of choice. */
    var removeEnabledTranscriptBlock = function(enabledTranscript) {
        var langCode = enabledTranscript['lang'];
        var langLabel = enabledTranscript['label'];
        var downloadUrl = enabledTranscript['url'];
        // Remove enabled transcript of choice
        var $enabledTranscriptBlock = $("div[value='" + langCode + "']").closest("div.enabled-default-transcripts-section");
        $enabledTranscriptBlock.remove();
        // Hide label of enabled transcripts if no such items left
        if (!$("div.enabled-default-transcripts-section:visible").length) {
            $("div.custom-field-section-label:contains('Enabled transcripts')").addClass('is-hidden');
        }
        // Add a transcript of choice to the list of available transcripts (xblock field Default Timed Transcript)
        var defaultTranscript= {'lang': langCode, 'label': langLabel, 'url': downloadUrl};
        createAvailableTranscriptBlock(defaultTranscript);
        // Create elements to display status messages on enabled transcript removal
        createStatusMessageElement(langCode, 'remove-default-transcript');
        // Display message with results on removal
        // Get all the currently enabled transcripts
        var allEnabledTranscripts = [];
        $('.enabled-default-transcripts-section .default-transcripts-label:visible').each(function(){
            var code = $(this).attr('value');
            allEnabledTranscripts.push(code);
        });
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
    };

    $defaultTranscriptUploader.click(function(event) {
        event.preventDefault();
        event.stopPropagation();
        var langCode = $(event.currentTarget).attr('data-lang-code');
        var label = $(event.currentTarget).attr('data-lang-label');
        var url = $(event.currentTarget).attr('data-download-url');
        // Remove a transcript of choice from the list of available ones
        var $availableTranscriptBlock = $("div[value='" + langCode + "']")
            .closest("div.available-default-transcripts-section:visible");
        $availableTranscriptBlock.remove();
        // Hide label of available transcripts if no such items left
        if (!$("div.available-default-transcripts-section:visible").length) {
            $("div.custom-field-section-label:contains('Available transcripts')").addClass('is-hidden');
        }
        // Create enabled transcript
        var default_transcript = {'lang': langCode, 'label' : label, 'url' : url};
        createEnabledTranscriptBlock(default_transcript);
    });

    $defaultTranscriptRemover.click(function(){
        var langCode = $(event.currentTarget).attr('data-lang-code');
        var langLabel = $(event.currentTarget).attr('data-lang-label');
        var downloadUrl = $(event.currentTarget).attr('data-download-url');
        var enabledTranscript = {'lang' : langCode, 'label' : langLabel, 'url': downloadUrl};
        removeEnabledTranscriptBlock(enabledTranscript);
    });

});
