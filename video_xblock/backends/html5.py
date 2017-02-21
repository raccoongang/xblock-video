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
            "controls": True,
            "preload": 'auto',
            "plugins": {
                "xblockEventPlugin": {},
                "offset": {
                    "start": context['start_time'],
                    "end": context['end_time'],
                    "current_time": context['player_state']['current_time'],
                },
            }
        })

        frag = super(Html5Player, self).get_frag(**context)
        frag.add_content(
            self.render_resource('static/html/html5.html', **context)
        )
        js_files = [
            'static/bower_components/videojs-offset/dist/videojs-offset.min.js'
        ]

        for js_file in js_files:
            frag.add_javascript(self.resource_string(js_file))

        return frag
