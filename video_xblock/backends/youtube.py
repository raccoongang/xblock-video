import re

from xblock.fragment import Fragment
from django.template import Template, Context

from video_xblock import BaseVideoPlayer, html_parser


class YoutubePlayer(BaseVideoPlayer):
    """
    YoutubePlayer is used for videos hosted on the Youtube.com
    """

    # http://regexr.com/3a2p0
    url_re = re.compile(r'(?:youtube\.com\/\S*(?:(?:\/e(?:mbed))?\/|watch\?(?:\S*?&?v\=))|youtu\.be\/)(?P<media_id>[a-zA-Z0-9_-]{6,11})')

    def media_id(self, href):
        return self.url_re.search(href).group('media_id')

    def get_frag(self, **context):
        html = Template(self.resource_string("../static/html/youtube.html"))
        frag = Fragment(
            html_parser.unescape(
                html.render(Context(context))
            )
        )

        frag.add_css(self.resource_string(
            '../static/bower_components/video.js/dist/video-js.min.css'
        ))
        frag.add_css(self.resource_string(
            '../static/css/videojs.css'
        ))
        frag.add_javascript(self.resource_string(
            '../static/bower_components/video.js/dist/video.min.js'
        ))
        frag.add_javascript(self.resource_string(
            '../static/video-speed.js'
        ))
        frag.add_javascript(self.resource_string(
            '../static/bower_components/videojs-youtube/dist/Youtube.min.js'
        ))
        frag.add_javascript(
            html_parser.unescape(
                Template(self.resource_string(
                        '../static/js/player_state.js'
                )).render(Context(context)))
        )

        return frag
