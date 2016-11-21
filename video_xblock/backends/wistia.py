import re

from xblock.fragment import Fragment
from django.template import Template, Context

from video_xblock import BaseVideoPlayer, html_parser


class WistiaPlayer(BaseVideoPlayer):
    """
    WistiaPlayer is used for videos hosted on the Wistia Video Cloud
    """

    # From official Wistia documentation. May change in the future
    # https://wistia.com/doc/construct-an-embed-code#the_regex
    url_re = re.compile(r'https?:\/\/(.+)?(wistia.com|wi.st)\/(medias|embed)\/(?P<media_id>.*)')

    def media_id(self, href):
        return self.url_re.search(href).group('media_id')

    def get_frag(self, **context):
        html = Template(self.resource_string("../static/html/wistiavideo.html"))
        frag = Fragment(
            html_parser.unescape(
                html.render(Context(context))
            )
        )
        frag.add_css(self.resource_string(
            '../static/bower_components/video.js/dist/video-js.min.css'
        ))
        frag.add_css(self.resource_string(
            '../static/wistia.css'
        ))
        frag.add_javascript(self.resource_string(
            '../static/bower_components/video.js/dist/video.min.js'
        ))
        frag.add_javascript(self.resource_string(
            '../static/video-speed.js'
        ))
        frag.add_javascript(self.resource_string(
            '../static/bower_components/videojs-wistia-extra/src/wistia.js'
        ))
        frag.add_javascript(
            html_parser.unescape(
                Template(self.resource_string(
                    '../static/js/player_state.js'
                )).render(Context(context)))
        )

        return frag
