# -*- coding: utf-8 -*-
"""Html5 Video player plugin."""

import json
import re

from video_xblock import BaseVideoPlayer


class Html5Player(BaseVideoPlayer):
    """
    Html5Player is used for videos by providing direct URL
    """

    url_re = re.compile(r'^(https?|ftp)://[^\s/$.?#].[^\s]*.(mpeg|mp4|ogg|webm)')

    metadata_fields = []

    # Html API for requesting transcripts.
    captions_api = {}

    def media_id(self, href):
        """
        Extract Platform's media id from the video url.

        E.g. https://example.wistia.com/medias/12345abcde -> 12345abcde
        """
        return href

    def get_type(self, href):
        """
        Get file extension for video.js type property.
        """
        return "video/" + self.url_re.search(href).groups()[-1]

    def get_frag(self, **context):
        """
        Return a Fragment required to render video player on the client side.
        """
        context['data_setup'] = json.dumps({
            "controlBar": {
                "volumeMenuButton": {
                    "inline": False,
                    "vertical": True
                }
            },
            "techOrder": ["html5"],
            "sources": [{
                "type": self.get_type(context['url']),
                "src": context['url']
            }],
            "playbackRates": [0.5, 1, 1.5, 2],
            "plugins": {
                "xblockEventPlugin": {},
                "offset": {
                    "start": context['start_time'],
                    "end": context['end_time'],
                    "current_time": context['player_state']['current_time'],
                },
            },
            "videoJSSpeedHandler": {},
        })

        frag = super(Html5Player, self).get_frag(**context)
        frag.add_content(
            self.render_resource('static/html/html5.html', **context)
        )
        js_files = [
            'static/bower_components/videojs-offset/dist/videojs-offset.min.js',
            'static/js/player-context-menu.js'
        ]

        for js_file in js_files:
            frag.add_javascript(self.resource_string(js_file))

        return frag

    def authenticate_api(self, **kwargs):  # pylint: disable=unused-argument
        """
        Current Vimeo captions API doesn't require authentication, but this may change.
        """
        return {}, ''

    def get_default_transcripts(self, **kwargs):  # pylint: disable=unused-argument
        """
        Fetch transcripts list from a video platform.
        """
        return [], ''

    def download_default_transcript(self, url, language_code):  # pylint: disable=unused-argument
        """
        Download default transcript in WebVVT format.
        """
        return u''
