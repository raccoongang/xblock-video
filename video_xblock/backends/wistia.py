import re

from xblock.fragment import Fragment

from video_xblock import BaseVideoPlayer


class WistiaPlayer(BaseVideoPlayer):
    """
    WistiaPlayer is used for videos hosted on the Wistia Video Cloud
    """

    # From official Wistia documentation. May change in the future
    # https://wistia.com/doc/construct-an-embed-code#the_regex
    url_re = re.compile(
        r'https?:\/\/(.+)?(wistia.com|wi.st)\/(medias|embed)\/(?P<media_id>.*)'
    )

    def media_id(self, href):
        return self.url_re.search(href).group('media_id')

    def get_frag(self, **context):
        frag = Fragment(
            self.render_resource('../static/html/wistiavideo.html', **context)
        )
        frag.add_css(self.resource_string(
            '../static/bower_components/video.js/dist/video-js.min.css'
        ))
        frag.add_css(self.resource_string(
            '../static/css/videojs.css'
        ))
        frag.add_css_url(
            'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css'
        )
        frag.add_javascript(self.resource_string(
            '../static/bower_components/video.js/dist/video.min.js'
        ))
        frag.add_javascript(self.resource_string(
            '../static/js/video-speed.js'
        ))
        frag.add_javascript(self.resource_string(
            '../static/bower_components/videojs-wistia-extra/src/wistia.js'
        ))
        frag.add_javascript(
            self.render_resource('../static/js/player_state.js', **context)
        )

        return frag
