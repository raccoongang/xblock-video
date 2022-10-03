/**
 * Update FullscreenToggle component and add the additional listener on toggling video fullscreen.
 */

(function() {
    'use strict';

    /**
     * Helper reports whether or not the document is currently displaying content in fullscreen mode.
     * @returns {boolean}
     */
    function isFullScreen() {
        if (typeof(document.fullscreenElement) === 'undefined') {
            if (document.webkitCurrentFullScreenElement == null) return false;
        }

        return document.fullscreenElement != null;
    }

    /**
     * Detect exit from the fullscreen mode and send a message to the parent window
     * about exiting fullscreen mode.
     */
    document.addEventListener('fullscreenchange', function () {
        if (window.parent !== window.top && !isFullScreen()) {
            // This is used by the Learning MFE to know about exiting fullscreen mode.
            // The MFE is then able to respond appropriately and scroll the window to the previous scroll position.
            window.top.postMessage({
                type: 'plugin.videoFullScreen',
                payload: {
                    open: false
                }
            }, '*');
        }
    });

    var fullscreenToggle = videojs.getComponent('FullscreenToggle');

    /**
     * Update the FullscreenToggle component for sending a message to the parent window
     * about entering fullscreen mode.
     */
    var FullscreenToggleExtended = videojs.extend(fullscreenToggle, {
        handleClick() {
            if (window.parent !== window.top && !this.player_.isFullscreen()) {
                // This is used by the Learning MFE to know about entering fullscreen mode.
                // The MFE is then able to respond appropriately and save the previous window scroll position.
                window.top.postMessage({
                    type: 'plugin.videoFullScreen',
                    payload: {
                        open: true
                    }
                }, '*');
            }

            if (!this.player_.isFullscreen()) {
                this.player_.requestFullscreen();
            } else {
                this.player_.exitFullscreen();
            }
        }
    });

    // Register the component under the name of the native one to rewrite it
    videojs.registerComponent('FullscreenToggle', FullscreenToggleExtended);
}).call(this);
