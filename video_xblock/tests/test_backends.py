"""
Test cases for video_xblock backends.
"""
import json
import copy
import requests
from ddt import ddt, data, unpack
from django.test.utils import override_settings
from xblock.core import XBlock
from video_xblock.settings import ALL_LANGUAGES
from video_xblock.utils import ugettext as _
from video_xblock.exceptions import VideoXBlockException
from video_xblock.tests.base import VideoXBlockTestBase
from video_xblock.backends import (
    brightcove,
    wistia,
    youtube,
    vimeo
)
from video_xblock.tests.mocks import (
    YoutubeAuthMock,
    WistiaAuthMock,
    BrightcoveAuthMock,
    VimeoAuthMock,
    YoutubeDefaultTranscriptsMock,
    BrightcoveDefaultTranscriptsMock
)


@ddt
class TestCustomBackends(VideoXBlockTestBase):
    """
    Unit tests for custom video xblock backends.
    """
    backends = ['youtube', 'brightcove', 'wistia', 'vimeo']

    @XBlock.register_temp_plugin(brightcove.BrightcovePlayer, 'brightcove')
    @XBlock.register_temp_plugin(wistia.WistiaPlayer, 'wistia')
    @XBlock.register_temp_plugin(youtube.YoutubePlayer, 'youtube')
    @XBlock.register_temp_plugin(vimeo.VimeoPlayer, 'vimeo')
    def setUp(self):
        super(TestCustomBackends, self).setUp()
        self.player = {}
        for backend in self.backends:
            player_class = XBlock.load_class(backend)
            self.player[backend] = player_class

    def test_get_player_html(self):
        """
        Check that player files content is returned in Response body.
        """
        context = {
            'player_state': {'transcripts': [], 'current_time': ''},
            'url': '',
            'start_time': '',
            'end_time': ''
        }
        for backend in self.backends:
            player = self.player[backend]
            res = player(self.xblock).get_player_html(**context)
            self.assertIn('window.videojs', res.body)

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
        for backend in self.backends:
            player = self.player[backend](self.xblock)
            default_transcripts = [{'lang': 'en'}, {'lang': 'ru'}, {'lang': 'uk'}]
            res = player.filter_default_transcripts(default_transcripts, transcripts)
            self.assertEqual(res, default)

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
        for backend in self.backends:
            player = self.player[backend](self.xblock)
            try:
                res = player.get_transcript_language_parameters(lng_abbr)
                self.assertEqual(res, (lng_abbr, lng_name))
            except VideoXBlockException as ex:
                self.assertIn(_('Not all the languages of transcripts fetched from video platform'), ex.message)

    @data(
        *zip(
            backends,
            [  # media urls
                'https://www.youtube.com/watch?v=VXJhzACm63Q',
                'https://studio.brightcove.com/products/videocloud/media/videos/45263567468485',
                'https://wi.st/medias/HRrr784kH8932Z',
                'https://vimeo.com/202889234'
            ],
            [  # expected media ids
                'VXJhzACm63Q', '45263567468485', 'HRrr784kH8932Z', '202889234'
            ]
        )
    )
    @unpack
    def test_media_id(self, backend, url, expected_media_id):
        """
        Check that media id is extracted from the video url.
        """
        player = self.player[backend](self.xblock)
        res = player.media_id(url)
        self.assertEqual(res, expected_media_id)

    @data(*zip(
        backends,
        [  # expected results per backend
            ('player_name',),
            ['account_id', 'player_id', 'token', 'player_name'],
            ('token', 'player_name'),
            ('player_name',)
        ]
    ))
    @unpack
    def test_customize_xblock_fields_display(self, backend, expected_result):
        """
        Check backend allows to edit only permitted fields.
        """
        editable_fields = ['account_id', 'player_id', 'token', 'player_name']
        player = self.player[backend]
        res = player.customize_xblock_fields_display(editable_fields)
        self.assertIsInstance(res, tuple)
        self.assertEqual(res[-1], expected_result)

    def apply_auth_mock(self, backend, event):
        """
        Save state of auth related entities before mocks are applied.
        """
        if backend == 'wistia':
            self.mocked_objects[backend] = {
                'obj': requests,
                'attrs': ['get', ],
                'value': [copy.copy(requests.get), ]
            }
            requests.get = WistiaAuthMock().get(event)
        elif backend == 'brightcove':
            self.mocked_objects[backend] = {
                'obj': brightcove.BrightcoveApiClient,
                'attrs': ['create_credentials', ],
                'value': [brightcove.BrightcoveApiClient.create_credentials, ]
            }
            brightcove.BrightcoveApiClient.create_credentials = BrightcoveAuthMock().create_credentials(event)
        else:
            # place here youtube and vimeo auth mocks assignments
            pass

    @data(*zip(
        backends,
        [  # tokens
            '', '', 'some_token', ''
        ],
        [  # events
            YoutubeAuthMock().get_events(),
            BrightcoveAuthMock().get_events(),
            WistiaAuthMock().get_events(),
            VimeoAuthMock().get_events(),
        ],
        [  # expected results
            YoutubeAuthMock().expected_value,
            BrightcoveAuthMock().expected_value,
            WistiaAuthMock().expected_value,
            VimeoAuthMock().expected_value
        ]
    ))
    @unpack
    def test_authenticate_api(self, backend, token, events, expected_result):
        """
        Check that backend can successfully pass authentication.
        """
        player = self.player[backend]
        for event in events:
            self.apply_auth_mock(backend, event)
            try:
                auth_data, error = res = player(self.xblock).authenticate_api(
                    **{'token': token, 'account_id': 45263567468485}
                )
                expected_auth_data = expected_result(event=event)[0]
                self.assertIsInstance(res, tuple)
                self.assertEqual(auth_data, expected_auth_data)
            except VideoXBlockException as ex:
                error = ex.message
            expected_error = expected_result(event=event)[-1]
            self.assertIn(expected_error, error)
#
#     @data(*zip(
#         backends,
#         [  # expected results
#             ({}, ''), ({}, 'Authentication to Brightcove API failed'), ({'token': None}, 'Authentication failed.')
#         ]
#     ))
#     @unpack
#     def test_authenticate_api_errors(self, backend, expected_result):
#         """
#         Make sure backend returns expected errors if wrong auth credentials provided.
#         """
#         player = self.player[backend]
#         auth_data, error = res = player().authenticate_api(account_id=0)
#         expected_auth_data = expected_result[0]
#         expected_error = expected_result[-1]
#         self.assertIsInstance(res, tuple)
#         self.assertEqual(auth_data, expected_auth_data)
#         self.assertIn(expected_error, error)
#
#     def apply_transcripts_mock(self, backend, event):
#         """
#         Save state of default transcripts related entities before mocks are applied.
#         """
#         player = self.player[backend]
#         if backend == 'wistia':
#             pass
#         elif backend == 'brightcove':
#             self.mocked_objects[backend] = {
#                 'obj': requests,
#                 'attrs': ['get', ],
#                 'value': [copy.copy(requests.get), ]
#             }
#             requests.get = BrightcoveDefaultTranscriptsMock(event)
#         else:
#             self.mocked_objects[backend] = {
#                 'obj': player,
#                 'attrs': ['fetch_default_transcripts_languages'],
#                 'value': [player.fetch_default_transcripts_languages]
#             }
#             player.fetch_default_transcripts_languages = YoutubeDefaultTranscriptsMock()\
#                 .fetch_default_transcripts_languages(event)
#
#     @override_settings(ALL_LANGUAGES=ALL_LANGUAGES)
#     @data(
#         *(
#             zip(
#                 backends,
#                 [  # video ids
#                     'PTaLj_Y9SRw', '45263567468485', 'jzmku8z83i'
#                 ],
#                 [  # mocked events
#                     ('status_not_200', 'empty_subs', 'cant_fetch_data', 'success'),
#                     ('fetch_transcripts_exception', 'text_tracks_not_in_response',
#                      'response_not_authorized', 'status_not_200', 'success'),
#                     tuple()
#                 ],
#                 [  # expected results per event
#                     (  # youtube results
#                         YoutubeDefaultTranscriptsMock().expected_value(event='status_not_200'),
#                         YoutubeDefaultTranscriptsMock().expected_value(event='empty_subs'),
#                         YoutubeDefaultTranscriptsMock().expected_value(event='cant_fetch_data'),
#                         YoutubeDefaultTranscriptsMock().expected_value(event='success')
#                     ),
#                     # (  # brightcove results
#                     #     BrightcoveDefaultTranscriptsMock().expected_value(event='fetch_transcripts_exception'),
#                     #     BrightcoveDefaultTranscriptsMock().expected_value(event='text_tracks_not_in_response'),
#                     #     BrightcoveDefaultTranscriptsMock().expected_value(event='response_not_authorized'),
#                     #     BrightcoveDefaultTranscriptsMock().expected_value(event='status_not_200'),
#                     #     BrightcoveDefaultTranscriptsMock().expected_value(event='success')
#                     # ),
#                     # ([], 'some_text')
#                 ]
#             )
#         )
#     )
#     @unpack
#     def test_get_default_transcripts(self, backend, video_id, events, expected_result):
#         player = self.player[backend]
#         for index, event in enumerate(events):
#             self.apply_transcripts_mock(backend, event)
#             default_transcripts, message = res = player().get_default_transcripts(video_id=video_id)
#             expected_default_transcripts = expected_result[index][0]
#             expected_message = expected_result[index][-1]
#             self.assertIsInstance(res, tuple)
#             self.assertEqual(default_transcripts, expected_default_transcripts)
#             self.assertIn(expected_message, message)
#         self.restore_mocked()
