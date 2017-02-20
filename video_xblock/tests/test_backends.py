"""
Test cases for video_xblock backends.
"""
# copy should be imported before requests
import copy
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
    VimeoDefaultTranscriptsMock,
    YoutubeDownloadTranscriptMock,
    BrightcoveDownloadTranscriptMock,
    WistiaDownloadTranscriptMock,
    VimeoDownloadTranscriptMock
)


@ddt
class TestCustomBackends(VideoXBlockTestBase):
    """
    Unit tests for custom video xblock backends.
    """
    backends = ['youtube', 'brightcove', 'wistia', 'vimeo']
    media_ids = ['44zaxzFsthY', '45263567468485', 'HRrr784kH8932Z', '202889234']
    media_urls = [
        'https://www.youtube.com/watch?v=44zaxzFsthY',
        'https://studio.brightcove.com/products/videocloud/media/videos/45263567468485',
        'https://wi.st/medias/HRrr784kH8932Z',
        'https://vimeo.com/202889234'
    ]
    auth_mocks = [
        YoutubeAuthMock(),
        BrightcoveAuthMock(),
        WistiaAuthMock(),
        VimeoAuthMock(),
    ]
    default_trans_mocks = [
        YoutubeDefaultTranscriptsMock(),
        BrightcoveDefaultTranscriptsMock(),
        WistiaDefaultTranscriptsMock(),
        VimeoDefaultTranscriptsMock(),
    ]

    download_transcript_mocks = [
        YoutubeDownloadTranscriptMock(),
        BrightcoveDownloadTranscriptMock(),
        WistiaDownloadTranscriptMock(),
        VimeoDownloadTranscriptMock(),
    ]

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
            media_urls,
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
            media_urls,
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

    @data(*zip(
        backends,
        ['some_token'] * len(backends),  # tokens
        auth_mocks,
    ))
    @unpack
    def test_authenticate_api(self, backend, token, auth_mock):
        """
        Check that backend can successfully pass authentication.
        """
        player = self.player[backend]
        for event in auth_mock.get_events():
            mock_obj = auth_mock.apply_mock(event)
            self.mocked_objects.append(mock_obj)
            try:
                auth_data, error = res = player(self.xblock).authenticate_api(
                    **{'token': token, 'account_id': 45263567468485}
                )
                expected_auth_data = auth_mock.expected_value(event)[0]
                self.assertIsInstance(res, tuple)
                self.assertEqual(auth_data, expected_auth_data)
            except VideoXBlockException as ex:
                error = ex.message
            expected_error = auth_mock.expected_value(event)[-1]
            self.assertIn(expected_error, error)

    @override_settings(ALL_LANGUAGES=ALL_LANGUAGES)
    @data(*(zip(
        backends,
        media_ids,  # video ids
        default_trans_mocks
    )))
    @unpack
    def test_get_default_transcripts(self, backend, video_id, trans_mock):
        player = self.player[backend]
        for event in trans_mock.get_events():
            mocked_object = trans_mock.apply_mock(event)
            if mocked_object:
                self.mocked_objects.append(mocked_object)
            if backend == 'brightcove':
                self.mocked_objects.append({
                    'obj': self.xblock,
                    'attrs': ['metadata', ],
                    'value': [copy.deepcopy(self.xblock.metadata), ]
                })
                self.xblock.metadata = BrightcoveDefaultTranscriptsMock(
                    mock_magic=self.xblock.metadata, event=event
                ).no_credentials()
            try:
                default_transcripts, message = res = player(self.xblock).get_default_transcripts(video_id=video_id)
                expected_default_transcripts = trans_mock.expected_value(event)[0]
                self.assertIsInstance(res, tuple)
                self.assertEqual(default_transcripts, expected_default_transcripts)
            except brightcove.BrightcoveApiClientError as ex:
                message = ex.message
            except babelfish.converters.LanguageReverseError:
                message = 'LanguageReverseError'
            expected_message = trans_mock.expected_value(event)[-1]
            self.assertIn(expected_message, message)
            self.restore_mocked()

    @data(
        *(
            zip(
                backends,
                download_transcript_mocks,
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
            )
        )
    )
    @unpack
    def test_download_default_transcript(self, backend, download_transcript_mock, params):
        """
        Check default transcript is downloaded from a video platform API.
        """
        player = self.player[backend]
        for index, event in enumerate(download_transcript_mock.get_events()):
            mocked_object = download_transcript_mock.apply_mock(event)
            self.mocked_objects.append(mocked_object)
            try:
                res = player(self.xblock).download_default_transcript(**params[index])
                message = ''
                expected_default_transcript = download_transcript_mock.expected_value(event)[0]
                self.assertIsInstance(res, unicode)
                self.assertEqual(res, expected_default_transcript)
            except VideoXBlockException as ex:
                message = ex.message
            except etree.XMLSyntaxError:
                message = 'XMLSyntaxError exception'
            expected_message = download_transcript_mock.expected_value(event)[-1]
            self.assertIn(expected_message, message)
            self.restore_mocked()
