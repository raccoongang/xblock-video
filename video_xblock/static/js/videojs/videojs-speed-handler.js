/**
 * This part is responsible for custom controlling of the playback rate.
 * Native videojs component's handlers are rewritten for the next events:
 * - ratechange
 * - click
 *
 */

(function() {
    'use strict';
    // Videojs 5/6 shim;
    var registerPlugin = videojs.registerPlugin || videojs.plugin;
    /**
        Videojs speed handler
    */
    function videoJSSpeedHandler(options) {
        var playbackRateMenuButton = videojs.getComponent('PlaybackRateMenuButton');
        var controlBar = videojs.getComponent('ControlBar');
        var videojsPlayer = videojs(window.videoPlayerId);

        /**
         * The custom component for controlling the playback rate.
         *
         * @param {Player|Object} player
         * @param {Object=} options
         * @extends PlaybackRateMenuButton
         * @class PlaybackRateMenuButtonExtended
         */
        var playbackRateMenuButtonExtended = videojs.extend(playbackRateMenuButton, {
            /** @constructor */
            constructor: function(player, options) {  // eslint-disable-line no-shadow
                playbackRateMenuButton.call(this, player, options);
                this.on('ratechange', this.updateLabel);
                this.on('click', this.handleClick);
            }
        });

        /**
         * Update Speed button label when rate is changed.
         * Undefined rate is replaced by significant value.
         *
         * @method updateLabel
         */
        playbackRateMenuButtonExtended.prototype.updateLabel = function() {
            var speed = this.player().playbackRate() || 1;
            this.labelEl_.innerHTML = speed + 'x';

            var playbackRateMenuItems = this.el_.children[0].querySelectorAll('.vjs-menu-item');

            playbackRateMenuItems.forEach((item) => {
                if (item.innerText === (speed + 'x')) {
                    item.classList.add('selected-item');
                } else {
                    item.classList.remove('selected-item');
                }
            })
        };

        /**
         * Handle click on Speed control.
         * Do nothing when control is clicked.
         *
         * @method handleClick
         */
        playbackRateMenuButtonExtended.prototype.handleClick = function() {
            // FIXME for Brightcove
            return false;
        };

        // Register the component under the name of the native one to rewrite it
        videojs.registerComponent('PlaybackRateMenuButton', playbackRateMenuButtonExtended);

        // Charge the component into videojs
        if (this.tagAttributes.brightcove !== undefined) {
            this.controlBar.customControlSpacer.addChild('PlaybackRateMenuButton', options);
            // Add the new component as a default player child
            videojsPlayer.addChild('PlaybackRateMenuButton');
        } else {
            controlBar.prototype.options_.children.push('PlaybackRateMenuButton');
        }
        return this;
    }
    // Export plugin to the root
    window.videoJSSpeedHandler = videoJSSpeedHandler;
    registerPlugin('videoJSSpeedHandler', videoJSSpeedHandler);
}).call(this);
