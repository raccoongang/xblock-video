"""
Test cases for video_xblock backends.
"""
import unittest
from ddt import ddt, data, unpack
from django.test.utils import override_settings
from video_xblock.backends.base import BaseVideoPlayer, VideoXBlockException
from video_xblock.settings import ALL_LANGUAGES
from video_xblock.utils import ugettext as _


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
