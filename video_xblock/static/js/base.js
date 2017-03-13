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

