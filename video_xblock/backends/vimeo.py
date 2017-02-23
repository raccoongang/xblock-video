# -*- coding: utf-8 -*-
"""Vimeo Video player plugin."""

import json
import re

from video_xblock import BaseVideoPlayer


class VimeoPlayer(BaseVideoPlayer):
    """
    VimeoPlayer is used for videos hosted on the Vimeo.com.
    """

    # Regex is taken from http://regexr.com/3a2p0
    # Reference: https://vimeo.com/153979733
    url_re = re.compile(r'https?:\/\/(.+)?(vimeo.com)\/(?P<media_id>.*)')

    # Vimeo API for requesting transcripts.
    captions_api = {}

    def media_id(self, href):
        """
        Extract Platform's media id from the video url.

        E.g. https://example.wistia.com/medias/12345abcde -> 12345abcde
        """
        return self.url_re.search(href).group('media_id')

    def get_frag(self, **context):
        """
        Return a Fragment required to render video player on the client side.
        """
        context['data_setup'] = json.dumps(VimeoPlayer.player_data_setup(context))

        frag = super(VimeoPlayer, self).get_frag(**context)
        frag.add_content(
            self.render_resource('static/html/vimeo.html', **context)
        )
        js_files = [
            'static/bower_components/videojs-vimeo/src/Vimeo.js',
            'static/bower_components/videojs-offset/dist/videojs-offset.min.js'
        ]

        for js_file in js_files:
            frag.add_javascript(self.resource_string(js_file))

        return frag

    @staticmethod
    def player_data_setup(context):
        """
        Vimeo Player data setup.
        """
        result = BaseVideoPlayer.player_data_setup(context).update({
            "techOrder": ["vimeo"],
            "sources": [{
                "type": "video/vimeo",
                "src": context['url']
            }],
            "vimeo": {"iv_load_policy": 1},
        })
        del result["playbackRates"]
        del result["plugins"]["videoJSSpeedHandler"]
        return result

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
