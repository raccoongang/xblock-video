import re

from xblock.fragment import Fragment
from django.template import Template, Context

from video_xblock import BaseVideoPlayer, html_parser


class BrightcovePlayer(BaseVideoPlayer):
    """
    BrightcovePlayer is used for videos hosted on the Brightcove Video Cloud
    """

    url_re = re.compile(r'https:\/\/studio.brightcove.com\/products\/videocloud\/media\/videos\/(?P<media_id>\d+)')

    def media_id(self, href):
        return self.url_re.match(href).group('media_id')

    def get_frag(self, **context):
        html = Template(self.resource_string("../static/html/brightcove.html"))
        frag = Fragment(
            html_parser.unescape(
                html.render(Context(context))
            )
        )
        frag.add_javascript(
            html_parser.unescape(
                Template(self.resource_string(
                    '../static/js/player_state.js'
                )).render(Context(context)))
        )

        return frag
