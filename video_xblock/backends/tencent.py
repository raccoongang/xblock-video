"""
Tencent Video player backend.
"""

import json
import logging
import re

from django.utils.translation import get_language
from xblock.fragment import Fragment

from video_xblock import BaseVideoPlayer
from video_xblock.utils import ugettext as _

log = logging.getLogger(__name__)


class TencentPlayer(BaseVideoPlayer):
    """
    TencentPlayer is used for videos hosted on tencent cloud.
    """

    url_re = re.compile(r'^([0-9]+)$')
    advanced_fields = []
    advanced_tab_enabled = False
    fields_help = {
        'href': _('Your FileID of the video to be played. E.g. 5285890799710670616'),
    }

    @property
    def basic_fields(self):
        """
        Tuple of VideoXBlock fields to display in Basic tab of edit modal window.

        Tencent videos require AppId.
        """
        return super().basic_fields + ['app_id']

    def validate_data(self, validation, data):
        """
        Validate app id value which is mandatory.

        Attributes:
            validation (xblock.validation.Validation): Object containing validation information for an xblock instance.
            data (xblock.internal.VideoXBlockWithMixins): Object containing data on xblock.
        """

        if not data.app_id:
            self.add_validation_message(
                validation,
                _("AppID can not be empty. Please provide a valid Tencent AppID.")
            )

    def media_id(self, href):
        """
        Return media_Id
        """
        return href

    def get_frag(self, **context):
        """
        Return a Fragment required to render video player on the client side.
        """
        context['player_state'] = json.dumps(context['player_state'])
        context['lang_code'] = get_language()

        frag = Fragment(
            self.render_template('tencent.html', **context)
        )
        frag.add_javascript(
            self.resource_string('static/js/base.js')
        )
        frag.add_javascript(
            self.render_resource('static/js/videojs/tencent-player-init.js', **context)
        )

        js_urls = [
            '//cloudcache.tencent-cloud.com/open/qcloud/video/tcplayer/libs/hls.min.0.12.4.js',
            '//cloudcache.tencent-cloud.com/open/qcloud/video/tcplayer/tcplayer.v4.min.js',
        ]
        for js_url in js_urls:
            frag.add_javascript_url(js_url)

        frag.add_css_url('//cloudcache.tencent-cloud.com/open/qcloud/video/tcplayer/tcplayer.css')

        return frag
