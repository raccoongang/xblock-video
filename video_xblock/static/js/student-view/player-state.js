/**
 * This part is responsible for loading and saving player state.
 * State includes:
 * - Current time
 * - Playback rate
 * - Volume
 * - Muted
 *
 * State is loaded after VideoJs player is fully initialized.
 * State is saved at certain events.
 */

var PlayerState = function(player, playerState) {
    'use strict';
    var xblockUsageId = getXblockUsageId();

    /** Create hashmap with all transcripts */
    var getTranscipts = function(transcriptsData) {
        var result = {};
        transcriptsData.forEach(function(transcript) {
            result[transcript.lang] = {
                label: transcript.label,
                url: transcript.url
            };
        });
        return result;
    };

    var transcripts = getTranscipts(playerState.transcripts);

    /** Restore default or previously saved player state */
    var setInitialState = function(state) {
        var stateCurrentTime = state.currentTime;
        var playbackProgress = localStorage.getItem('playbackProgress');
        if (playbackProgress) {
            playbackProgress = JSON.parse(playbackProgress);
            if (playbackProgress[window.videoPlayerId]) {
                stateCurrentTime = playbackProgress[window.videoPlayerId];
            }
        }
        if (stateCurrentTime > 0) {
            player.currentTime(stateCurrentTime);
        }
        player.volume(state.volume);
        player.muted(state.muted);
        player.playbackRate(state.playbackRate);
        player.captionsLanguage = state.captionsLanguage;  // eslint-disable-line no-param-reassign
        // To switch off transcripts and captions state if doesn`t have transcripts with current captions language
        if (!transcripts[player.captionsLanguage]) {
            player.captionsEnabled = player.transcriptsEnabled = false; // eslint-disable-line no-param-reassign
        } else {
            player.transcriptsEnabled = state.transcriptsEnabled; // eslint-disable-line no-param-reassign
            player.captionsEnabled = state.captionsEnabled; // eslint-disable-line no-param-reassign
        }
    };

    /**
     * Save player state by posting it in a message to parent frame.
     * Parent frame passes it to a server by calling VideoXBlock.save_state() handler.
     */
    var saveState = function() {
        var playerObj = this;
        var transcriptUrl = getDownloadTranscriptUrl(transcripts, playerObj);

        var newState = {
            volume: playerObj.volume(),
            currentTime: playerObj.ended() ? 0 : playerObj.currentTime(),
            playbackRate: playerObj.playbackRate(),
            muted: playerObj.muted(),
            transcriptsEnabled: playerObj.transcriptsEnabled,
            captionsEnabled: playerObj.captionsEnabled,
            captionsLanguage: playerObj.captionsLanguage
        };
        if (JSON.stringify(newState) !== JSON.stringify(playerState)) {
            console.log('Starting saving player state');  // eslint-disable-line no-console
            playerState = newState; // eslint-disable-line no-param-reassign
            parent.postMessage(
                {
                    action: 'saveState',
                    info: newState,
                    xblockUsageId: xblockUsageId,
                    xblockFullUsageId: getXblockFullUsageId(),
                    downloadTranscriptUrl: transcriptUrl || '#'
                },
                document.location.protocol + '//' + document.location.host
            );
        }
    };

    /**
     *  Save player progress in browser's local storage.
     *  We need it when user is switching between tabs.
     */
    var saveProgressToLocalStore = function() {
        var playerObj = this;
        var playbackProgress;
        playbackProgress = JSON.parse(localStorage.getItem('playbackProgress') || '{}');
        playbackProgress[window.videoPlayerId] = playerObj.ended() ? 0 : playerObj.currentTime();
        localStorage.setItem('playbackProgress', JSON.stringify(playbackProgress));
    };

    setInitialState(playerState);

    /** Post real-time currentTime/duration to parent so the progress bar updates every tick */
    var sendRealtimeProgress = function() {
        var currentTime = player.currentTime();
        var duration = player.duration();
        if (duration > 0) {
            parent.postMessage(
                {
                    action: 'progressUpdate',
                    xblockUsageId: xblockUsageId,
                    info: { current_time: currentTime, duration: duration }
                },
                document.location.protocol + '//' + document.location.host
            );
        }
    };

    player.on('timeupdate', saveProgressToLocalStore);
    player.on('timeupdate', sendRealtimeProgress);
    player.on('volumechange', saveState);
    player.on('ratechange', saveState);
    player.on('play', saveState);
    player.on('pause', saveState);
    player.on('ended', saveState);
    player.on('transcriptstatechanged', saveState);
    player.on('captionstatechanged', saveState);
    player.on('languagechange', saveState);

    /**
     * Send a watch-progress ping to the parent frame every 5 seconds while playing.
     * The parent frame forwards it to the `update_progress` XBlock handler.
     */
    var PROGRESS_PING_INTERVAL_MS = 5000;
    var progressInterval = null;

    var sendProgressPing = function() {
        var playerObj = player;
        var currentTime = playerObj.currentTime();
        var duration = playerObj.duration();
        if (duration > 0) {
            parent.postMessage(
                {
                    action: 'updateProgress',
                    xblockUsageId: xblockUsageId,
                    xblockFullUsageId: getXblockFullUsageId(),
                    info: {
                        current_time: currentTime,
                        duration: duration
                    }
                },
                document.location.protocol + '//' + document.location.host
            );
        }
    };

    player.on('play', function() {
        if (!progressInterval) {
            progressInterval = setInterval(sendProgressPing, PROGRESS_PING_INTERVAL_MS);
        }
    });

    player.on('pause', function() {
        // Send one final ping on pause so progress is not lost between intervals
        sendProgressPing();
        clearInterval(progressInterval);
        progressInterval = null;
    });

    player.on('ended', function() {
        // Send a ping with duration as current_time to ensure 100% progress is recorded,
        // since currentTime() may already be 0 if the player loops immediately after ending.
        var duration = player.duration();
        if (duration > 0) {
            parent.postMessage(
                {
                    action: 'updateProgress',
                    xblockUsageId: xblockUsageId,
                    xblockFullUsageId: getXblockFullUsageId(),
                    info: {
                        current_time: duration,
                        duration: duration
                    }
                },
                document.location.protocol + '//' + document.location.host
            );
        }
        clearInterval(progressInterval);
        progressInterval = null;
    });
};

domReady(function() {
    'use strict';
    videojs(window.videoPlayerId).ready(function() {
        PlayerState(this, window.playerStateObj);
    });
});
