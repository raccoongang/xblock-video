/**
 * This part is responsible for creation of captions and transcripts buttons on player load.
 */
domReady(function() {
    'use strict';

    videojs(window.videoPlayerId).ready(function() {
        var enableTrack = false;
        var player_ = this;
        var frozen = false;
        var autoScrolling = true;
        var CAPTIONS_FREEZE_TIME = 10000;
        var cssClasses = 'vjs-custom-caption-button vjs-menu-button vjs-menu-button-popup vjs-control vjs-button';
        // attach the widget to the page
        var transcriptContainer = document.getElementById('transcript');
        var captionContainer = document.getElementsByClassName('vjs-text-track-display');
        /** This function is wrapper for initial Brightcove's captions. */
        var initCaptions = function initCaptions() {
            var transcript;
            var tracks = player_.textTracks().tracks_;
            tracks.forEach(function(track) {
                if (track.kind === 'captions') {
                    if (track.language === player_.captionsLanguage) {
                        track.mode = 'showing';  // eslint-disable-line no-param-reassign
                        enableTrack = true;
                    } else {
                        track.mode = 'disabled';  // eslint-disable-line no-param-reassign
                    }
                }
            });
            if (!enableTrack && tracks[0].kind === 'captions') {
                tracks[0].mode = 'showing';
            }
            // fire up the plugin
            transcript = player_.transcript({
                showTrackSelector: false,
                showTitle: false,
                followPlayerTrack: true,
                tabIndex: 10,
                scrollToCenter: true
            });
            transcript.el().addEventListener('click', function() {
                player_.trigger('transcriptstatechanged');
            });

            // Show or hide the transcripts block depending on the transcript state
            if (!player_.transcriptsEnabled) {
                transcriptContainer.className += ' is-hidden';
            }
            transcriptContainer.appendChild(transcript.el());
        };

        if (this.tagAttributes.brightcove !== undefined) {
            // This branch for brightcove player
            this.one('loadedmetadata', initCaptions);
        } else {
            initCaptions();
        }

        this.on('transcriptenabled', function() {
            transcriptContainer.classList.remove('is-hidden');
            this.transcriptsEnabled = true;
            this.trigger('transcriptstatechanged');

            parent.postMessage({
                action: 'transcript',
                type: 'transcriptenabled',
            }, document.location.protocol + '//' + document.location.host);

            var transcriptContainerItem = transcriptContainer.querySelectorAll('.transcript-line');
            // Add listening events for transcript's children lines for pausing and starting auto scrolling
            Array.from(transcriptContainerItem).forEach(function(line) {
                line.addEventListener('focusin', captionFocus);
                line.addEventListener('focusout', captionBlur);
                line.addEventListener('keydown', captionKeyDown);
            });
        });
        this.on('transcriptdisabled', function() {
            transcriptContainer.classList.add('is-hidden');
            this.transcriptsEnabled = false;
            this.trigger('transcriptstatechanged');

            parent.postMessage({
                action: 'transcript',
                type: 'transcriptdisabled',
            }, document.location.protocol + '//' + document.location.host);
        });

        // Show or hide the captions block depending on the caption state
        if (!this.captionsEnabled) {
            Array.from(captionContainer).forEach(function(caption) {
                caption.className += ' is-hidden';  // eslint-disable-line no-param-reassign
            });
        }
        this.on('captionenabled', function() {
            Array.from(captionContainer).forEach(function(caption) {
                caption.classList.toggle('is-hidden', false);
            });
            this.captionsEnabled = true;
            this.trigger('captionstatechanged');
        });
        this.on('captiondisabled', function() {
            Array.from(captionContainer).forEach(function(caption) {
                caption.classList.toggle('is-hidden', true);
            });
            this.captionsEnabled = false;
            this.trigger('captionstatechanged');
        });
        if (this.captionsEnabled) {
            cssClasses += ' vjs-control-enabled';
        }
        this.toggleButton({
            style: 'fa-cc',
            enabledEvent: 'captionenabled',
            disabledEvent: 'captiondisabled',
            cssClasses: cssClasses,
            tabIndex: 6
        });
        cssClasses = 'vjs-custom-transcript-button vjs-menu-button vjs-menu-button-popup vjs-control vjs-button';
        if (this.transcriptsEnabled) {
            cssClasses += ' vjs-control-enabled';
        }
        this.toggleButton({
            style: 'fa-quote-left',
            enabledEvent: 'transcriptenabled',
            disabledEvent: 'transcriptdisabled',
            cssClasses: cssClasses,
            tabIndex: 7
        });

        // Add listening events for transcripts block for pausing and starting auto scrolling
        transcriptContainer.addEventListener('mouseenter', onMouseEnter);
        transcriptContainer.addEventListener('mouseleave', onMouseLeave);
        transcriptContainer.addEventListener('mousemove', onMouseEnter);
        transcriptContainer.addEventListener('mousewheel', onMouseEnter);
        transcriptContainer.addEventListener('DOMMouseScroll', onMouseEnter);

        // Update transcripts scroll position on player time update.
        player_.on('timeupdate', scrollCaption);

        // Freezes moving of captions when mouse is over them.
        function onMouseEnter() {
            if (frozen) {
                clearTimeout(frozen);
            }

            frozen = setTimeout(onMouseLeave, CAPTIONS_FREEZE_TIME);
        }

        // Unfreezes moving of captions when mouse go out.
        function onMouseLeave() {
            if (frozen) {
                clearTimeout(frozen);
            }

            frozen = null;
        }

        // Scrolls caption container to make active caption visible.
        function scrollCaption() {
            // Automatic scrolling gets disabled if one of the captions has
            // received focus through tabbing.
            if (!frozen && player_.transcriptsEnabled && autoScrolling) {
                var transcriptContainer = document.getElementById('transcript');
                var el = transcriptContainer.querySelector('.is-active');
                transcriptContainer.scrollTo({
                    top: calculateOffset(el),
                });
            }
        }

        // Calculates offset for paddings.
        function calculateOffset(element) {
            var transcriptContainer = document.getElementById('transcript');
            var captionHeight = transcriptContainer.offsetHeight;
            return element ? element.offsetTop - captionHeight / 2 : 0;
        }

        // Handles focus event on concrete caption.
        function captionFocus() {
            // If the focus comes from tabbing, turn off automatic scrolling.
            autoScrolling = false;
        }

        // Handles blur event on concrete caption.
        function captionBlur() {
            // Continue auto scrolling if focus move out from the transcript block.
            autoScrolling = true;
        }

        // Handles keydown event on concrete caption.
        function captionKeyDown(event) {
            var time = event.target.getAttribute('data-begin');

            if (event.which === 13 && time) { // Enter key
                player_.currentTime(time);
            }
        }
    });
});
