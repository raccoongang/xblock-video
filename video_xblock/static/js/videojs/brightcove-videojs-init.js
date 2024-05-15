/**
 * This part is responsible for initialization of Video.js and custom JS plugins in Brightcove player.
 */

domReady(function() {
    'use strict';
    // Videojs 5/6 shim
    var registerPlugin = videojs.registerPlugin || videojs.plugin;
    var player = videojs(window.videoPlayerId);
    window.videojs = videojs;

    registerPlugin('xblockEventPlugin', window.xblockEventPlugin);
    player.xblockEventPlugin();

    registerPlugin('xblockCompletionPlugin', window.xblockCompletionPlugin);
    player.xblockCompletionPlugin({
        completionEnabled: true,
        startTime: window.playerStartTime,
        endTime: window.playerEndTime,
        isComplete: false, // TODO: should be replaced with dynamic data from the Backend
    });

    registerPlugin('offset', window.vjsoffset);
    player.offset({
        start: window.playerStartTime,
        end: window.playerEndTime,
    });
});
