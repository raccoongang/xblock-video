/** Run a callback when DOM is fully loaded */
var domReady = function(callback) {
    'use strict';
    if (document.readyState === 'interactive' || document.readyState === 'complete') {
        callback();
    } else {
        document.addEventListener('DOMContentLoaded', callback);
    }
};

/**
 * Get python context and fill in js global variables with it
 */
window.videoPlayerId = '{{ video_player_id }}';
window.playerStateObj = JSON.parse('{{ player_state }}');

