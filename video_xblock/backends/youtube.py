import re

from video_xblock import BaseVideoPlayer


class YoutubePlayer(BaseVideoPlayer):
    """
    YoutubePlayer is used for videos hosted on the Youtube.com
    """

    # http://regexr.com/3a2p0
    url_re = re.compile(r'(?:youtube\.com\/\S*(?:(?:\/e(?:mbed))?\/|watch\?(?:\S*?&?v\=))|youtu\.be\/)(?P<media_id>[a-zA-Z0-9_-]{6,11})')

    def media_id(self, href):
        return self.url_re.search(href).group('media_id')

    def get_frag(self, **context):
        frag = super(YoutubePlayer, self).get_frag()
        frag.add_content(
            self.render_resource('../static/html/youtube.html', **context)
        )

        frag.add_javascript(self.resource_string(
            '../static/bower_components/videojs-youtube/dist/Youtube.min.js'
        ))

        return frag
