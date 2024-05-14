/** Run a callback when DOM is fully loaded */
var domReady = function(callback) {
    'use strict';
    if (document.readyState === 'interactive' || document.readyState === 'complete') {
        callback();
    } else {
        document.addEventListener('DOMContentLoaded', callback);
    }
};

/** Get XblockUsageId from xblock's url. */
var getXblockUsageId = function() {
    'use strict';
    return window.location.hash.slice(1);
};

/** Get XblockFullUsageId id from xblock's url. */
var getXblockFullUsageId = function() {
    'use strict';
    var startIdx = window.location.pathname.indexOf('/xblock/') + '/xblock/'.length;
    var endIdx = window.location.pathname.indexOf('/handler/');

    return window.location.pathname.slice(startIdx, endIdx);
};

/** Get transcript url for current caption language */
var getDownloadTranscriptUrl = function(transcripts, player) {
    'use strict';
    var downloadTranscriptUrl;
    if (transcripts[player.captionsLanguage]) {
        downloadTranscriptUrl = transcripts[player.captionsLanguage].url;
    }
    return downloadTranscriptUrl;
};
