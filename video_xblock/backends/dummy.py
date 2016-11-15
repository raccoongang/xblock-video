import re

from xblock.fragment import Fragment
from video_xblock import BaseVideoPlayer


class DummyPlayer(BaseVideoPlayer):
    """
    DummyPlayer is used as a placeholder for those cases when appropriate
    player cannot be displayed.
    """
    url_re = re.compile(r'')

    def get_frag(self, **context):
        return Fragment(u'[Here be Video]')

    def media_id(self, href):
        return '<media_id>'
