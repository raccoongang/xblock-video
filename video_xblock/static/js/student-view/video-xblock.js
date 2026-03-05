/**
 * Javascript for VideoXBlock.student_view()
 * @param runtime Runtime object.
 * @param element xblock's html element. Or object which contains html block we needed as element[0].
 */
function VideoXBlockStudentViewInit(runtime, element) {
    'use strict';

    let baseColor = getComputedStyle(document.documentElement).getPropertyValue('--base-color');
    let iframes = document.querySelectorAll('.video-iframe');

    iframes.forEach((iframe) => {
        iframe.addEventListener('load', () => {
            let root = iframe.contentWindow.document.querySelector(':root');
            root.style.setProperty('--base-color', baseColor);
        });
    });

    var xblockElement = typeof(element[0]) !== 'undefined' ? element[0] : element;
    var stateHandlerUrl = runtime.handlerUrl(xblockElement, 'save_player_state');
    var eventHandlerUrl = runtime.handlerUrl(xblockElement, 'publish_event');
    var progressHandlerUrl = runtime.handlerUrl(xblockElement, 'update_progress');
    var downloadTranscriptHandlerUrl = runtime.handlerUrl(xblockElement, 'download_transcript');
    var usageId = (
        xblockElement.attributes['data-usage-id'] ||  // Open edX runtime
        xblockElement.attributes['data-usage']  // Workbench runtime
    ).value;
    window.videoXBlockState = window.videoXBlockState || {};
    var handlers = window.videoXBlockState.handlers =  // eslint-disable-line vars-on-top
        window.videoXBlockState.handlers || {
            saveState: {},
            analytics: {},
            downloadTranscriptChanged: {},
            updateProgress: {}
        };
    handlers.saveState[usageId] = stateHandlerUrl;
    handlers.analytics[usageId] = eventHandlerUrl;
    handlers.updateProgress[usageId] = progressHandlerUrl;
    /** Update the watch progress display below the video */
    // function updateProgressDisplay(watchProgress) {
    //     var pct = Math.round(watchProgress * 100);
    //     // usageId may be the full usage key (e.g. block-v1:...+block@HASH) or just the short HASH.
    //     // The progress bar element uses only the short block hash as its id suffix.
    //     var blockId = usageId.indexOf('+block@') !== -1 ? usageId.split('+block@').pop() : usageId;
    //     var progressEl = document.getElementById('video-watch-progress-' + blockId);
    //     if (!progressEl) { return; }
    //     var bar = progressEl.querySelector('.video-watch-progress-bar');
    //     var label = progressEl.querySelector('.video-watch-progress-value');
    //     if (bar) { bar.style.width = pct + '%'; }
    //     if (label) { label.textContent = pct + '%'; }
    // }

    /** Send data to server by POSTing it to appropriate VideoXBlock handler */
    function sendData(handlerUrl, data, isProgressUpdate) {
        $.ajax({
            type: 'POST',
            url: handlerUrl,
            data: JSON.stringify(data)
        })
        .done(function(response) {
            console.log('Data processed successfully.');  // eslint-disable-line no-console
            // if (isProgressUpdate && response && typeof response.watch_progress !== 'undefined') {
            //     updateProgressDisplay(response.watch_progress);
            // }
        })
        .fail(function() {
            console.log('Failed to process data');  // eslint-disable-line no-console
        });
    }
    if (!window.videoXBlockListenerRegistered) {
        // Make sure we register event listener only once even if there are more than
        // one VideoXBlock on a page
        window.addEventListener('message', receiveMessage, false);  // eslint-disable-line no-use-before-define
        window.videoXBlockListenerRegistered = true;
    }
    /**
        * Receive a message from child frames.
        * Expects a specific type of messages containing video player state to be saved on a server.
        * Pass the sate to `saveState()` for handling.
    */
    function receiveMessage(event) {
        // For Chrome, the origin property is in the event.originalEvent object.
        var origin = event.origin || event.originalEvent.origin;
        if ((origin !== document.location.protocol + '//' + document.location.host) ||
            (event.data.action === undefined)) {
            // Discard malformed or a message received from another domain
            return;
        }
        try {
            if (event.data.action === 'transcript') {
                var iframeWrapper = document.querySelector('.video-iframe-holder');
                event.data.type === 'transcriptenabled'
                    ? iframeWrapper.classList.add('transcriptenabled')
                    : iframeWrapper.classList.remove('transcriptenabled');
                return;
            }
            if (event.data.action === 'downloadTranscriptChanged') {
                // eslint-disable-next-line no-use-before-define
                updateTranscriptDownloadUrl(event.data.downloadTranscriptUrl);
            }
            // Real-time client-side progress bar update (no server call)
            if (event.data.action === 'progressUpdate') {
                var info = event.data.info;
                if (info && info.duration > 0) {
                    updateProgressDisplay(info.current_time / info.duration);
                }
                return;
            }
            var action = handlers[event.data.action];
            var url = action[event.data.xblockUsageId] || action[event.data.xblockFullUsageId];  // eslint-disable-line vars-on-top
            if (url) {
                sendData(url, event.data.info, event.data.action === 'updateProgress');
            }
        } catch (err) {
            console.log(err);  // eslint-disable-line no-console
        }
    }
    /** Updates transcript download url if it is enabled */
    function updateTranscriptDownloadUrl(downloadTranscriptUrl) {
        var downloadLinkEl = document.getElementById('download-transcript-button');
        var link;
        if (downloadLinkEl) {
            link = downloadLinkEl.getElementsByTagName('a')[0];
            if (downloadTranscriptUrl) {
                link.href = downloadTranscriptHandlerUrl + '?' + downloadTranscriptUrl;
                downloadLinkEl.classList.remove('is-hidden');
            } else {
                link.href = '#';
                downloadLinkEl.classList.add('is-hidden');
            }
        }
    }
}
