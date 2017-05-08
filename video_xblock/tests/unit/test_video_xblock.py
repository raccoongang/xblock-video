"""
Test cases for video_xblock.
"""

import datetime
import json
from mock import patch, Mock, MagicMock, PropertyMock

from django.test import RequestFactory
from django.conf import settings
from xblock.fragment import Fragment

from video_xblock import VideoXBlock
from video_xblock.utils import ugettext as _
from video_xblock.tests.unit.base import VideoXBlockTestBase
from video_xblock.tests.unit.mocks.base import MockCourse

from video_xblock.constants import PlayerName


settings.configure()


class VideoXBlockTests(VideoXBlockTestBase):
    """
    Test cases for video_xblock.
    """

    def test_fields_xblock(self):
        """
        Test xblock fields consistency with their default values.
        """

        self.assertEqual(self.xblock.display_name, _('Video'))
        self.assertEqual(self.xblock.href, '')
        self.assertEqual(self.xblock.account_id, 'account_id')
        self.assertEqual(self.xblock.player_id, 'default')
        self.assertEqual(self.xblock.player_name, PlayerName.DUMMY)
        self.assertEqual(self.xblock.start_time, datetime.timedelta(seconds=0))
        self.assertEqual(self.xblock.end_time, datetime.timedelta(seconds=0))
        self.assertEqual(self.xblock.current_time, 0)
        self.assertEqual(self.xblock.playback_rate, 1)
        self.assertEqual(self.xblock.volume, 1)
        self.assertEqual(self.xblock.muted, False)
        self.assertEqual(self.xblock.captions_language, '')
        self.assertEqual(self.xblock.transcripts_enabled, False)
        self.assertEqual(self.xblock.captions_enabled, False)
        self.assertEqual(self.xblock.handout, '')
        self.assertEqual(self.xblock.transcripts, '')
        self.assertEqual(self.xblock.download_transcript_allowed, False)
        self.assertEqual(self.xblock.download_video_allowed, False)
        self.assertEqual(self.xblock.download_video_url, '')

    def test_player_state(self):
        """
        Test player state property.
        """
        self.xblock.course_id = 'test:course:id'
        self.xblock.runtime.modulestore = Mock(get_course=MockCourse)
        self.assertDictEqual(
            self.xblock.player_state,
            {
                'currentTime': self.xblock.current_time,
                'muted': self.xblock.muted,
                'playbackRate': self.xblock.playback_rate,
                'volume': self.xblock.volume,
                'transcripts': [],
                'transcriptsEnabled': self.xblock.transcripts_enabled,
                'captionsEnabled': self.xblock.captions_enabled,
                'captionsLanguage': 'en',
                'transcriptsObject': {}
            }
        )

    def test_get_brightcove_js_url(self):
        """
        Test brightcove.js url generation.
        """
        self.assertEqual(
            VideoXBlock.get_brightcove_js_url(self.xblock.account_id, self.xblock.player_id),
            "https://players.brightcove.net/{account_id}/{player_id}_default/index.min.js".format(
                account_id=self.xblock.account_id,
                player_id=self.xblock.player_id
            )
        )

    def test_save_player_state(self):
        """
        Test player state saving.
        """
        self.xblock.course_id = 'test:course:id'
        self.xblock.runtime.modulestore = Mock(get_course=MockCourse)
        data = {
            'currentTime': 5,
            'muted': True,
            'playbackRate': 2,
            'volume': 0.5,
            'transcripts': [],
            'transcriptsEnabled': True,
            'captionsEnabled': True,
            'captionsLanguage': 'ru',
            'transcriptsObject': {}
        }
        factory = RequestFactory()
        request = factory.post('', json.dumps(data), content_type='application/json')

        response = self.xblock.save_player_state(request)

        self.assertEqual('{"success": true}', response.body)  # pylint: disable=no-member
        self.assertDictEqual(self.xblock.player_state, {
            'currentTime': data['currentTime'],
            'muted': data['muted'],
            'playbackRate': data['playbackRate'],
            'volume': data['volume'],
            'transcripts': data['transcripts'],
            'transcriptsEnabled': data['transcriptsEnabled'],
            'captionsEnabled': data['captionsEnabled'],
            'captionsLanguage': data['captionsLanguage'],
            'transcriptsObject': {}
        })

    @patch('video_xblock.video_xblock.render_resource')
    @patch('video_xblock.video_xblock.resource_string')
    @patch.object(VideoXBlock, 'route_transcripts')
    def test_studio_view(self, route_transcripts, resource_string_mock, render_resource_mock):
        # Arrange
        unused_context_stub = object()
        render_resource_mock.return_value = u'<iframe/>'
        handler_url = self.xblock.runtime.handler_url = Mock()
        handler_url.side_effect = ['/player/url', '/transcript/download/url']
        route_transcripts.return_value = 'transcripts.vtt'

        # Act
        studio_view = self.xblock.student_view(unused_context_stub)

        # Assert
        self.assertIsInstance(studio_view, Fragment)
        render_resource_mock.assert_called_once_with(
            'static/html/student_view.html',
            display_name='Video',
            download_transcript_allowed=False,
            download_video_url=False,
            handout='',
            handout_file_name='',
            player_url='/player/url',
            transcript_download_link='',
            transcripts='transcripts.vtt',
            usage_id='deprecated_string'
        )
        resource_string_mock.assert_called_with('static/css/student-view.css')
        handler_url.assert_called_with(self.xblock, 'download_transcript')
        route_transcripts.assert_called_once_with(self.xblock.transcripts)
