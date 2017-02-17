"""
Test cases for video_xblock backends.
"""
# copy should be imported before requests
import copy
import requests
import babelfish
from ddt import ddt, data, unpack
from lxml import etree
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
    BrightcoveDefaultTranscriptsMock,
    WistiaDefaultTranscriptsMock,
    YoutubeDownloadTranscriptMock,
    BrightcoveDownloadTranscriptMock,
    WistiaDownloadTranscriptMock
)


@ddt
class TestCustomBackends(VideoXBlockTestBase):
    """
    Unit tests for custom video xblock backends.
    """
    backends = ['youtube', 'brightcove', 'wistia', 'vimeo']
    media_ids = ['44zaxzFsthY', '45263567468485', 'HRrr784kH8932Z', '202889234']

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
            'player_state': {
                'transcripts': [{
                    'lang': 'en',
                    'label': 'English',
                    'url': 'http://test.url'
                }],
                'current_time': ''
            },
            'url': '',
            'start_time': '',
            'end_time': ''
        }
        for backend in self.backends:
            player = self.player[backend]
            res = player(self.xblock).get_player_html(**context)
            self.assertIn('window.videojs', res.body)

    @data(
        *zip(
            backends,
            [  # media urls
                'https://www.youtube.com/watch?v=44zaxzFsthY',
                'https://studio.brightcove.com/products/videocloud/media/videos/45263567468485',
                'https://wi.st/medias/HRrr784kH8932Z',
                'https://vimeo.com/202889234'
            ],
        )
    )
    @unpack
    def test_match(self, backend, url):
        """
        Check if provided video `href` validates in right way.
        """
        player = self.player[backend]
        res = player.match(url)
        self.assertTrue(bool(res))

        # test wrong data
        res = player.match('http://wrong.url')
        self.assertFalse(bool(res))

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
                'https://www.youtube.com/watch?v=44zaxzFsthY',
                'https://studio.brightcove.com/products/videocloud/media/videos/45263567468485',
                'https://wi.st/medias/HRrr784kH8932Z',
                'https://vimeo.com/202889234'
            ],
            media_ids  # expected media ids
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
            self.mocked_objects.append({
                'obj': requests,
                'attrs': ['get', ],
                'value': [copy.deepcopy(requests.get), ]
            })
            requests.get = WistiaAuthMock(event=event).get()
        elif backend == 'brightcove':
            self.mocked_objects.append({
                'obj': brightcove.BrightcoveApiClient,
                'attrs': ['create_credentials', ],
                'value': [brightcove.BrightcoveApiClient.create_credentials, ]
            })
            brightcove.BrightcoveApiClient.create_credentials = BrightcoveAuthMock(event=event).create_credentials()
        else:
            # place here youtube and vimeo auth mocks assignments
            pass

    @data(*zip(
        backends,
        [  # tokens
            'some_token', 'some_token', 'some_token', 'some_token'
        ],
        [  # mocked events
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
                expected_auth_data = expected_result(event)[0]
                self.assertIsInstance(res, tuple)
                self.assertEqual(auth_data, expected_auth_data)
            except VideoXBlockException as ex:
                error = ex.message
            expected_error = expected_result(event)[-1]
            self.assertIn(expected_error, error)

    def apply_transcripts_mock(self, backend, event):
        """
        Save state of default transcripts related entities before mocks are applied.
        """
        player = self.player[backend]
        if backend == 'youtube':
            self.mocked_objects.append({
                'obj': player,
                'attrs': ['fetch_default_transcripts_languages'],
                'value': [player.fetch_default_transcripts_languages, ]
            })
            player.fetch_default_transcripts_languages = YoutubeDefaultTranscriptsMock(event=event)\
                .fetch_default_transcripts_languages()
        elif backend == 'brightcove':
            self.mocked_objects.append({
                'obj': brightcove.BrightcoveApiClient,
                'attrs': ['get', ],
                'value': [copy.deepcopy(brightcove.BrightcoveApiClient.get), ]
            })
            self.mocked_objects.append({
                'obj': self.xblock,
                'attrs': ['metadata', ],
                'value': [copy.deepcopy(self.xblock.metadata), ]
            })
            self.xblock.metadata = BrightcoveDefaultTranscriptsMock(
                mock_magic=self.xblock.metadata, event=event
            ).no_credentials()
            brightcove.BrightcoveApiClient.get = BrightcoveDefaultTranscriptsMock(
                mock_magic=brightcove.BrightcoveApiClientError, event=event
            ).api_client_get()
        elif backend == 'wistia':
            self.mocked_objects.append({
                'obj': requests,
                'attrs': ['get', ],
                'value': [copy.deepcopy(requests.get), ]
            })
            requests.get = WistiaDefaultTranscriptsMock(
                mock_magic=requests.exceptions.RequestException, event=event
            ).get()
        else:
            # vimeo
            pass

    @override_settings(ALL_LANGUAGES=ALL_LANGUAGES)
    @data(
        *(
            zip(
                backends,
                media_ids,  # video ids
                [  # mocked events
                    YoutubeDefaultTranscriptsMock().get_events(),
                    BrightcoveDefaultTranscriptsMock().get_events(),
                    WistiaDefaultTranscriptsMock().get_events(),
                    # for vimeo we add at least one random event to test returned result while no logic present
                    ['get_transcripts']
                ],
                [  # expected results per event
                    YoutubeDefaultTranscriptsMock().expected_value,
                    BrightcoveDefaultTranscriptsMock().expected_value,
                    WistiaDefaultTranscriptsMock().expected_value,
                    lambda x: ([], '')
                ]
            )
        )
    )
    @unpack
    def test_get_default_transcripts(self, backend, video_id, events, expected_result):
        player = self.player[backend]
        for event in events:
            self.apply_transcripts_mock(backend, event)
            try:
                default_transcripts, message = res = player(self.xblock).get_default_transcripts(video_id=video_id)
                expected_default_transcripts = expected_result(event)[0]
                self.assertIsInstance(res, tuple)
                self.assertEqual(default_transcripts, expected_default_transcripts)
            except brightcove.BrightcoveApiClientError as ex:
                message = ex.message
            except babelfish.converters.LanguageReverseError:
                message = 'LanguageReverseError'
            expected_message = expected_result(event)[-1]
            self.assertIn(expected_message, message)
            self.restore_mocked()

    def apply_download_mock(self, backend, event):
        """
        Save state of download transcript related entities before mocks are applied.
        """
        player = self.player[backend]
        if backend == 'wistia':
            self.mocked_objects.append({
                'obj': player,
                'attrs': ['default_transcripts', ],
                'value': [copy.deepcopy(player.default_transcripts), ]
            })
            player.default_transcripts = WistiaDownloadTranscriptMock(event=event).get()
        elif backend == 'brightcove':
            self.mocked_objects.append({
                'obj': requests,
                'attrs': ['get', ],
                'value': [copy.deepcopy(requests.get), ]
            })
            requests.get = BrightcoveDownloadTranscriptMock(event=event).get()
        elif backend == 'youtube':
            self.mocked_objects.append({
                'obj': requests,
                'attrs': ['get', ],
                'value': [copy.deepcopy(requests.get), ]
            })
            requests.get = YoutubeDownloadTranscriptMock(event=event).get()
        else:
            # place here vimeo mocks assignments
            pass

    @data(
        *(
            zip(
                backends,
                [  # mocked events
                    YoutubeDownloadTranscriptMock().get_events(),
                    BrightcoveDownloadTranscriptMock().get_events(),
                    WistiaDownloadTranscriptMock().get_events(),
                    ('success', )
                ],
                [  # params
                    (  # youtube
                        {'url': None, 'language_code': None},
                        {'url': 'http://example.com', 'language_code': ''},
                        {'url': 'http://example.com', 'language_code': ''}
                    ),
                    (  # brightcove
                        {'url': None, 'language_code': None},
                        {'url': 'http://example.com', 'language_code': 'en'}
                    ),
                    (  # wistia
                        {'url': None, 'language_code': None},
                        {'url': 'http://example.com', 'language_code': 'en'},
                        {'url': 'http://example.com', 'language_code': 'uk'}
                    ),
                    (  # vimeo
                        {'url': None, 'language_code': None},
                    )
                ],
                [  # expected results per event
                    YoutubeDownloadTranscriptMock().expected_value,
                    BrightcoveDownloadTranscriptMock().expected_value,
                    WistiaDownloadTranscriptMock().expected_value,
                    lambda x: ('', '')
                ]
            )
        )
    )
    @unpack
    def test_download_default_transcript(self, backend, events, params, expected_result):
        """
        Check default transcript is downloaded from a video platform API.
        """
        player = self.player[backend]
        for index, event in enumerate(events):
            self.apply_download_mock(backend, event)
            try:
                res = player(self.xblock).download_default_transcript(**params[index])
                message = ''
                expected_default_transcript = expected_result(event)[0]
                self.assertIsInstance(res, unicode)
                self.assertEqual(res, expected_default_transcript)
            except VideoXBlockException as ex:
                message = ex.message
            except etree.XMLSyntaxError:
                message = 'XMLSyntaxError exception'
            expected_message = expected_result(event)[-1]
            self.assertIn(expected_message, message)
            self.restore_mocked()
