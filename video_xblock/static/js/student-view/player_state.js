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

var PlayerState = function(playerObj, playerStateObj) {
    'use strict';
    this.player = playerObj;
    this.player_state = {
        volume: playerStateObj.volume,
        currentTime: playerStateObj.current_time,
        playbackRate: playerStateObj.playback_rate,
        muted: playerStateObj.muted,
        transcriptsEnabled: playerStateObj.transcripts_enabled,
        captionsEnabled: playerStateObj.captions_enabled,
        captionsLanguage: playerStateObj.captions_language
    };

    /** Create hashmap with all transcripts */
    this.getTranscipts = function(transcripts) {
        var result = {};
        transcripts.forEach(function(transcript) {
            result[transcript.lang] = {
                label: transcript.label,
                url: transcript.url
            };
        });
        return result;
    };
    this.transcripts = this.getTranscipts(playerStateObj.transcripts);

    /** Restore default or previously saved player state */
    this.setInitialState = function(state) {
        var stateCurrentTime = state.currentTime;
        var playbackProgress = localStorage.getItem('playbackProgress');
        if (playbackProgress) {
            playbackProgress = JSON.parse(playbackProgress);
            if (playbackProgress[window.videoPlayerId]) {
                stateCurrentTime = playbackProgress[window.videoPlayerId];
            }
        }
        if (stateCurrentTime > 0) {
            this.player.currentTime(stateCurrentTime);
        }
        this.player
            .volume(state.volume)
            .muted(state.muted)
            .playbackRate(state.playbackRate);
        this.player.transcriptsEnabled = state.transcriptsEnabled;
        this.player.captionsEnabled = state.captionsEnabled;
        this.player.captionsLanguage = state.captionsLanguage;
        // To switch off transcripts and captions state if doesn`t have transcripts with current captions language
        if (!this.transcripts[this.player.captionsLanguage]) {
            this.player.captionsEnabled = this.player.transcriptsEnabled = false;
        }
    };

    /**
     *  Add new triggers to player's events
     */
    this.initTriggers = function() {
        /**
         * Save player state by posting it in a message to parent frame.
         * Parent frame passes it to a server by calling VideoXBlock.save_state() handler.
         */
        var playerState = this.player_state;
        var xblockUsageId = getXblockUsageId();
        var transcripts = this.transcripts;

        /** Get transcript url for current caption language */
        var getDownloadTranscriptUrl = function(player) {
            var downloadTranscriptUrl;
            if (transcripts[player.captionsLanguage]) {
                downloadTranscriptUrl = transcripts[player.captionsLanguage].url;
            } else {
                downloadTranscriptUrl = '#';
            }
            return downloadTranscriptUrl;
        };

        /**
         * Save player state by posting it in a message to parent frame.
         * Parent frame passes it to a server by calling VideoXBlock.save_state() handler.
         */
        var saveState = function() {
            var player = this;
            var newState = {
                volume: player.volume(),
                currentTime: player.ended() ? 0 : player.currentTime(),
                playbackRate: player.playbackRate(),
                muted: player.muted(),
                transcriptsEnabled: player.transcriptsEnabled,
                captionsEnabled: player.captionsEnabled,
                captionsLanguage: player.captionsLanguage
            };
            if (JSON.stringify(newState) !== JSON.stringify(playerState)) {
                console.log('Starting saving player state');  // eslint-disable-line no-console
                playerState = newState;
                parent.postMessage({
                    action: 'saveState',
                    info: newState,
                    xblockUsageId: xblockUsageId,
                    downloadTranscriptUrl: getDownloadTranscriptUrl(player)
                },
                document.location.protocol + '//' + document.location.host
                );
            }
        };

        /**
         *  Save player progress in browser's local storage.
         *  We need it when user is switching between tabs.
         */
        var saveProgressToLocalStore = function saveProgressToLocalStore() {
            var player = this;
            var playbackProgress = localStorage.getItem('playbackProgress');
            if (!playbackProgress) {
                playbackProgress = '{}';
            }
            playbackProgress = JSON.parse(playbackProgress);
            playbackProgress[window.videoPlayerId] = player.ended() ? 0 : player.currentTime();
            localStorage.setItem('playbackProgress', JSON.stringify(playbackProgress));
        };

        this.player
            .on('timeupdate', saveProgressToLocalStore)
            .on('volumechange', saveState)
            .on('ratechange', saveState)
            .on('play', saveState)
            .on('pause', saveState)
            .on('ended', saveState)
            .on('transcriptstatechanged', saveState)
            .on('captionstatechanged', saveState)
            .on('languagechange', saveState);
    };
    this.setInitialState(this.player_state);
    this.initTriggers();
};

domReady(function() {
    'use strict';
    videojs(window.videoPlayerId).ready(function() {
        PlayerState(this, window.playerStateObj);
    });
});
