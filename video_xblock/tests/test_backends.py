"""
Test cases for video_xblock backends.
"""
import unittest
import json
import copy
import requests
from ddt import ddt, data, unpack
from django.test.utils import override_settings
from xblock.core import XBlock
from video_xblock.backends.base import BaseVideoPlayer, VideoXBlockException
from video_xblock.settings import ALL_LANGUAGES
from video_xblock.utils import ugettext as _
from video_xblock.backends import (
    brightcove,
    wistia,
    youtube
)
from video_xblock.tests.mocks import WistiaAuthMock, BrightcoveAuthMock


# pylint: disable=abstract-class-instantiated
@ddt
class TestAbstractBaseBackend(unittest.TestCase):
    """
    Unit tests for abstract base backend of video_xblock.
    """

    def setUp(self):
        # allow abstract class to be instantiated
        BaseVideoPlayer.__abstractmethods__ = set()

        self.instance = BaseVideoPlayer()
        self.context = {
            'player_state': {'transcripts': []}
        }
        self.path = '../static/html/base.html'
        super(TestAbstractBaseBackend, self).setUp()

    def test_render_resource(self):
        """
        Check template is rendered using provided context.
        """
        regexp = r'^<html>([a-zA-Z0-9\s\\n<>\/]+)?<\/html>$'
        res = self.instance.render_resource(self.path, **self.context)
        self.assertRegexpMatches(res, regexp)

    def test_add_js_content(self):
        """
        Check that `add_js_content` method encapsulates provided javascript code in <script> tags.
        """
        regexp = r'^<script>([a-zA-Z0-9\s\\n<>\/]+)?<\/script>$'

        res = self.instance.add_js_content(self.path, **self.context)
        self.assertRegexpMatches(res, regexp)

    def test_get_player_html(self):
        """
        Check that player files content is returned in Response body.
        """
        res = self.instance.get_player_html(**self.context)
        self.assertIn('window.videojs', res.body)

    def test_match_class_method(self):
        """
        Should always return `None`.
        """
        res = BaseVideoPlayer.match('http://example.com')
        self.assertIsNone(res)

    @override_settings(ALL_LANGUAGES=ALL_LANGUAGES)
    @data(
        ('en', 'English'),
        ('to', 'Tonga (Tonga Islands)'),
        ('unknown', '')
    )
    @unpack
    def test_get_transcript_language_parameters(self, lng_abbr, lng_name):
        """
        Check parameters of the transcript's language.
        """
        try:
            res = BaseVideoPlayer.get_transcript_language_parameters(lng_abbr)
            self.assertEqual(res, (lng_abbr, lng_name))
        except VideoXBlockException as ex:
            self.assertIn(_('Not all the languages of transcripts fetched from video platform'), ex.message)

    @data(
        ([{'lang': 'ru'}], [{'lang': 'en'}, {'lang': 'uk'}]),
        ([{'lang': 'en'}, {'lang': 'uk'}], [{'lang': 'ru'}]),
        ([{'lang': 'some_other_lng'}], [{'lang': 'en'}, {'lang': 'ru'}, {'lang': 'uk'}])
    )
    @unpack
    def test_filter_default_transcripts(self, transcripts, default):
        """
        Check transcripts are excluded from the list of available ones in video xblock.
        """
        default_transcripts = [{'lang': 'en'}, {'lang': 'ru'}, {'lang': 'uk'}]
        res = BaseVideoPlayer.filter_default_transcripts(default_transcripts, transcripts)
        self.assertEqual(res, default)


@ddt
class TestCustomBackends(unittest.TestCase):
    """
    Unit tests for custom video xblock backends.
    """
    backends = ['youtube', 'brightcove', 'wistia']

    @XBlock.register_temp_plugin(brightcove.BrightcovePlayer, 'brightcove')
    @XBlock.register_temp_plugin(wistia.WistiaPlayer, 'wistia')
    @XBlock.register_temp_plugin(youtube.YoutubePlayer, 'youtube')
    def setUp(self):
        self.player = {}
        self.mocked_objects = []
        context = {
            'data_setup': json.dumps({
                "controlBar": {"volumeMenuButton": {"inline": False, "vertical": True}},
                "playbackRates": [0.5, 1.0, 1.5, 2.0],
                "plugins": {
                    "xblockEventPlugin": {},
                    "offset": {"start": '0:0:0', "end": '1:0:20', "current_time": '0:0:0'},
                    "videoJSSpeedHandler": {},
                }
            }),
            'player_state': {'transcripts': []}
        }
        for backend in self.backends:
            player_class = XBlock.load_class(backend)
            self.player[backend] = {
                'class': player_class,
                'context': context
            }
        super(TestCustomBackends, self).setUp()

    @data(
        *zip(
            backends,
            [
                'https://www.youtube.com/watch?v=VXJhzACm63Q',
                'https://studio.brightcove.com/products/videocloud/media/videos/45263567468485',
                'https://wi.st/medias/HRrr784kH8932Z'
            ],
            ['VXJhzACm63Q', '45263567468485', 'HRrr784kH8932Z']
        )
    )
    @unpack
    def test_media_id(self, backend, url, media_id):
        """
        Check that media id is extracted from the video url.
        """
        player = self.player[backend]['class']()
        res = player.media_id(url)
        self.assertEqual(res, media_id)

    @data(*zip(
        backends,
        [  # expected results per backend
            ('player_name',),
            ['account_id', 'player_id', 'token', 'player_name'],
            ('token', 'player_name')
        ]
    ))
    @unpack
    def test_customize_xblock_fields_display(self, backend, expected_result):
        """
        Check backend allows to edit only permitted fields.
        """
        editable_fields = ['account_id', 'player_id', 'token', 'player_name']
        player = self.player[backend]['class']
        res = player.customize_xblock_fields_display(editable_fields)
        self.assertIsInstance(res, tuple)
        self.assertEqual(res[-1], expected_result)

    def apply_auth_mock(self, backend):
        """
        Save state of auth related entities before mocks are applied.
        """
        player = self.player[backend]['class']
        if backend == 'wistia':
            self.mocked_objects.append({
                'obj': requests,
                'attrs': ['get', ],
                'value': [copy.copy(requests.get), ]
            })
            requests.get = WistiaAuthMock()
        elif backend == 'brightcove':
            self.mocked_objects.append({
                'obj': player,
                'attrs': ['get_client_credentials', 'get_access_token'],
                'value': [player.get_client_credentials, player.get_access_token]
            })
            player.get_client_credentials = BrightcoveAuthMock().get_client_credentials()
            player.get_access_token = BrightcoveAuthMock().get_access_token()
        else:
            # place here youtube auth mock assignment
            pass

    def restore_mocked(self):
        """
        Restore state of mocked entities.
        """
        if self.mocked_objects:
            for original in self.mocked_objects:
                for index, attr in enumerate(original['attrs']):
                    setattr(original['obj'], attr, original['value'][index])
            self.mocked_objects = []

    @data(*zip(
        backends,
        ['', '', 'some_token'],
        [({}, ''), (BrightcoveAuthMock.expected_value(), ''), (WistiaAuthMock.expected_value(token='some_token'), '')]
    ))
    @unpack
    def test_authenticate_api(self, backend, token, expected_result):
        """
        Check that backend can successfully pass authentication.
        """
        player = self.player[backend]['class']
        self.apply_auth_mock(backend)
        auth_data, error = res = player().authenticate_api(**{'token': token, 'account_id': 45263567468485})
        expected_auth_data = expected_result[0]
        expected_error = expected_result[-1]
        self.assertIsInstance(res, tuple)
        self.assertEqual(auth_data, expected_auth_data)
        self.assertIn(expected_error, error)
        self.restore_mocked()

    @data(*zip(
        backends,
        [({}, ''), ({}, 'Authentication to Brightcove API failed'), ({'token': None}, 'Authentication failed.')]
    ))
    @unpack
    def test_authenticate_api_errors(self, backend, expected_result):
        """
        Make sure backend returns expected errors if wrong auth credentials provided.
        """
        player = self.player[backend]['class']
        auth_data, error = res = player().authenticate_api(account_id=0)
        expected_auth_data = expected_result[0]
        expected_error = expected_result[-1]
        self.assertIsInstance(res, tuple)
        self.assertEqual(auth_data, expected_auth_data)
        self.assertIn(expected_error, error)

    @data(
        *(
            zip(
                backends,
                ['cFnqX6V21h4', '45263567468485', 'jzmku8z83i'],
                [([], 'doesn\'t have any timed transcript'), ([], 'sdgd'), ([], 'fgs')]
            ) + zip(
                backends,
                ['', '', ''],
                [([], 'No timed transcript may be fetched'), ([], 'dfgd'), ([], 'Invalid credentials')]
            )
        )
    )
    @unpack
    def test_get_default_transcripts(self, backend, video_id, expected_result):
        player = self.player[backend]['class']
        default_transcripts, message = res = player().get_default_transcripts(video_id=video_id, token='')
        expected_default_transcripts = expected_result[0]
        expected_message = expected_result[-1]
        self.assertIsInstance(res, tuple)
        self.assertEqual(default_transcripts, expected_default_transcripts)
        self.assertIn(expected_message, message)
