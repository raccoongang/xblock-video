"""
Brightcove Video player plugin
"""

import re

from xblock.fragment import Fragment

from video_xblock import BaseVideoPlayer


class BrightcovePlayer(BaseVideoPlayer):
    """
    BrightcovePlayer is used for videos hosted on the Brightcove Video Cloud.
    """

    url_re = re.compile(r'https:\/\/studio.brightcove.com\/products\/videocloud\/media\/videos\/(?P<media_id>\d+)')

    def media_id(self, href):
        """
        Brightcove specific implementation of BaseVideoPlayer.media_id()
        """
        return self.url_re.match(href).group('media_id')

    def get_frag(self, **context):
        """
        Compose an XBlock fragment with video player to be rendered in student view.

        Brightcove backend is a special case and doesn't use vanila Video.js player.
        Because of this it doesn't use `super.get_frag()`
        """

        frag = Fragment(
            self.render_resource('../static/html/brightcove.html', **context)
        )
        frag.add_css_url(
            'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css'
        )
        frag.add_content(
            self.add_js_content('../static/js/player_state.js', **context)
        )
        frag.add_content(
            self.add_js_content('../static/js/toggle-button.js')
        )
        if context['player_state']['transcripts']:
            frag.add_content(
                self.add_js_content('../static/bower_components/videojs-transcript/dist/videojs-transcript.js')
            )
            frag.add_content(
                self.add_js_content('../static/js/videojs-transcript.js', **context)
            )
        frag.add_content(
            self.add_js_content('../static/js/videojs-tabindex.js', **context)
        )
        frag.add_content(
            self.add_js_content('../static/js/videojs_event_plugin.js', **context)
        )
        frag.add_content(
            self.add_js_content('../static/bower_components/videojs-offset/dist/videojs-offset.js')
        )
        frag.add_content(
            self.add_js_content('../static/js/videojs-speed-handler.js', **context)
        )
        frag.add_content(
            self.add_js_content('../static/js/brightcove-videojs-init.js', **context)
        )
        frag.add_css(
            self.resource_string('../static/css/brightcove.css')
        )
        frag.add_css(
            self.resource_string('../static/css/transcripts.css')
        )
        return frag
