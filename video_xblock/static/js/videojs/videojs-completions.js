/**
 * This part is responsible for completion of the video player.
 */
(function() {
    'use strict';
    /**
     * Videojs plugin.
     * Listens for progress and send event to parent frame to be processed as a completion request
     * @param {Object} options - Plugin options passed in at initialization time.
     */
    function XBlockCompletionPlugin(options) {
        var player = this;
        this.options = options;
        this.lastSentTime = undefined;
        this.isComplete = this.options.isComplete;
        this.completionPercentage = this.options.completionPercentage || 0.95;
        this.startTime = this.options.startTime;
        this.endTime = this.options.endTime;
        this.isEnabled = this.options.completionEnabled;

        /** Determine what point in the video (in seconds from the beginning) counts as complete. */
        this.calculateCompleteAfterTime = function(startTime, endTime) {
            return (endTime - startTime) * this.completionPercentage;
        };

        /** How many seconds to wait after a POST fails to try again. */
        this.repostDelaySeconds = function() {
            return 3.0;
        };

        if (this.endTime) {
            this.completeAfterTime = this.calculateCompleteAfterTime(this.startTime, this.endTime);
        }

        if (this.isEnabled) {
            /** Event handler to check if the video is complete, and submit
             *  a completion if it is.
             *
             *  If the timeupdate handler doesn't fire after the required
             *  percentage, this will catch any fully complete videos.
             */
            player.on('ended', function() {
                player.handleEnded();
            });

            /** Event handler to check video progress, and mark complete if
             *  greater than completionPercentage
             */
            player.on('timeupdate', function() {
                player.handleTimeUpdate(player.currentTime());
            });
        }

        /** Handler to call when the ended event is triggered */
        this.handleEnded = function() {
            if (this.isComplete) {
                return;
            }
            this.markCompletion();
        };

        /** Handler to call when a timeupdate event is triggered */
        this.handleTimeUpdate = function(currentTime) {
            var duration;

            if (this.isComplete) {
                return;
            }

            if (this.lastSentTime !== undefined && currentTime - this.lastSentTime < this.repostDelaySeconds()) {
                // Throttle attempts to submit in case of network issues
                return;
            }

            if (this.completeAfterTime === undefined) {
                // Duration is not available at initialization time
                duration = player.duration();
                if (!duration) {
                    // duration is not yet set. Wait for another event,
                    // or fall back to 'ended' handler.
                    return;
                }
                this.completeAfterTime = this.calculateCompleteAfterTime(this.startTime, duration);
            }

            if (currentTime > this.completeAfterTime) {
                this.markCompletion(currentTime);
            }
        };

        /** Send event to parent frame to be processed as a completion request */
        this.markCompletion =  function(currentTime) {
            this.isComplete = true;
            this.lastSentTime = currentTime;
            parent.postMessage({
                action: 'completions',
                info: { completion: 1.0 },
                xblockUsageId: getXblockUsageId(),
                xblockFullUsageId: getXblockFullUsageId(),
            }, document.location.protocol + '//' + document.location.host);
        };

        return this;
    }
    window.xblockCompletionPlugin = XBlockCompletionPlugin;
    // add plugin if player has already initialized
    if (window.videojs) {
        window.videojs.plugin('xblockCompletionPlugin', xblockCompletionPlugin);  // eslint-disable-line no-undef
    }
}).call(this);
