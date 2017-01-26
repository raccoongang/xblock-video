"""
Dummy Video player plugin
"""

import re

from xblock.fragment import Fragment
from video_xblock import BaseVideoPlayer


class DummyPlayer(BaseVideoPlayer):
    """
    DummyPlayer is a placeholder for cases when appropriate player can't be displayed.
    """
    url_re = re.compile(r'')

    def get_frag(self, **context):  # pylint: disable=unused-argument
        return Fragment(u'[Here be Video]')

    def media_id(self, href):  # pylint: disable=unused-argument
        return '<media_id>'

    def captions_api(self):
        return {}

    def get_default_transcripts(self, **kwargs):  # pylint: disable=unused-argument
        return []

    def customize_xblock_fields_display(self):
        pass
