"""
VideoXBlock mixins test cases.
"""

from mock import patch, Mock, PropertyMock

from xblock.exceptions import NoSuchServiceError

from video_xblock.constants import DEFAULT_LANG
from video_xblock.tests.base import VideoXBlockTestBase
from video_xblock.utils import loader
from video_xblock.video_xblock import VideoXBlock


class ContentStoreMixinTest(VideoXBlockTestBase):
    """Test ContentStoreMixin"""

    @patch('video_xblock.mixins.import_from')
    def test_contentstore_no_service(self, import_mock):
        import_mock.return_value = 'contentstore_test'

        self.assertEqual(self.xblock.contentstore, 'contentstore_test')
        import_mock.assert_called_once_with('xmodule.contentstore.django', 'contentstore')

    @patch('video_xblock.mixins.import_from')
    def test_static_content_no_service(self, import_mock):
        import_mock.return_value = 'StaticContent_test'

        self.assertEqual(self.xblock.static_content, 'StaticContent_test')
        import_mock.assert_called_once_with('xmodule.contentstore.content', 'StaticContent')

    def test_contentstore(self):
        with patch.object(self.xblock, 'runtime') as runtime_mock:
            service_mock = runtime_mock.service
            type(service_mock.return_value).contentstore = cs_mock = PropertyMock(
                return_value='contentstore_test'
            )

            self.assertEqual(self.xblock.contentstore, 'contentstore_test')
            service_mock.assert_called_once_with(self.xblock, 'contentstore')
            cs_mock.assert_called_once()

    def test_static_content(self):
        with patch.object(self.xblock, 'runtime') as runtime_mock:
            service_mock = runtime_mock.service
            type(service_mock.return_value).StaticContent = sc_mock = PropertyMock(
                return_value='StaticContent_test'
            )

            self.assertEqual(self.xblock.static_content, 'StaticContent_test')
            service_mock.assert_called_once_with(self.xblock, 'contentstore')
            sc_mock.assert_called_once()


class LocationMixinTests(VideoXBlockTestBase):
    """Test LocationMixin"""

    def test_xblod_doesnt_have_location_by_default(self):
        self.assertFalse(hasattr(self.xblock, 'location'))

    def test_fallback_block_id(self):
        self.assertEqual(self.xblock.block_id, 'block_id')

    def test_fallback_course_key(self):
        self.assertEqual(self.xblock.course_key, 'course_key')

    def test_fallback_deprecated_string(self):
        self.assertEqual(self.xblock.deprecated_string, 'deprecated_string')

    def test_block_id(self):
        self.xblock.location = Mock()
        type(self.xblock.location).block_id = block_mock = PropertyMock(
            return_value='test_block_id'
        )

        self.assertEqual(self.xblock.block_id, 'test_block_id')
        block_mock.assert_called_once()

    def test_course_key(self):
        self.xblock.location = Mock()

        type(self.xblock.location).course_key = course_key_mock = PropertyMock(
            return_value='test_course_key'
        )

        self.assertEqual(self.xblock.course_key, 'test_course_key')
        course_key_mock.assert_called_once()

    def test_deprecated_string(self):
        self.xblock.location = Mock()
        self.xblock.location.to_deprecated_string = str_mock = Mock(
            return_value='test_str'
        )

        self.assertEqual(self.xblock.deprecated_string, 'test_str')
        str_mock.assert_called_once()


class PlaybackStateMixinTests(VideoXBlockTestBase):
    """Test PlaybackStateMixin"""

    def test_fallback_course_default_language(self):
        self.xblock.runtime = runtime_mock = Mock()
        runtime_mock.service = service_mock = Mock(side_effect=NoSuchServiceError)

        self.assertEqual(self.xblock.course_default_language, DEFAULT_LANG)
        service_mock.assert_called_once()

    def test_course_default_language(self):
        self.xblock.runtime = runtime_mock = Mock()
        service_mock = runtime_mock.service
        lang_mock = type(service_mock.return_value.get_course.return_value).language = PropertyMock(
            return_value='test_lang'
        )
        lang_mock.return_value = 'test_lang'
        self.xblock.course_id = course_id_mock = PropertyMock()

        self.assertEqual(self.xblock.course_default_language, 'test_lang')
        service_mock.assert_called_once_with(self.xblock, 'modulestore')
        lang_mock.assert_called_once()
        course_id_mock.assert_not_called()


class TranscriptsMixinTests(VideoXBlockTestBase):
    """Test TranscriptsMixin"""

    @patch('video_xblock.mixins.WebVTTWriter.write')
    @patch('video_xblock.mixins.detect_format')
    def test_convert_caps_to_vtt(self, detect_format_mock, vtt_writer_mock):
        detect_format_mock.return_value.return_value.read = read_mock = Mock()
        read_mock.return_value = 'non vtt transcript'
        vtt_writer_mock.return_value = 'vtt transcript'

        self.assertEqual(self.xblock.convert_caps_to_vtt('test caps'), 'vtt transcript')
        vtt_writer_mock.assert_called_once_with('non vtt transcript')

    @patch('video_xblock.mixins.WebVTTWriter.write')
    @patch('video_xblock.mixins.detect_format')
    def test_convert_caps_to_vtt_fallback(self, detect_format_mock, vtt_writer_mock):
        detect_format_mock.return_value = None

        self.assertEqual(self.xblock.convert_caps_to_vtt('test caps'), u'')
        vtt_writer_mock.assert_not_called()
        detect_format_mock.assert_called_once_with('test caps')

    @patch.object(VideoXBlock, 'captions_language', new_callable=PropertyMock)
    @patch.object(VideoXBlock, 'transcripts', new_callable=PropertyMock)
    def test_get_transcript_download_link(self, trans_mock, lang_mock):
        lang_mock.return_value = 'en'
        trans_mock.return_value = '[{"lang": "en", "url": "test_transcript.vtt"}]'

        self.assertEqual(self.xblock.get_transcript_download_link(), 'test_transcript.vtt')

    @patch.object(VideoXBlock, 'transcripts', new_callable=PropertyMock)
    def test_get_transcript_download_link_fallback(self, trans_mock):
        trans_mock.return_value = ''

        self.assertEqual(self.xblock.get_transcript_download_link(), '')


class WorkbenchMixinTest(VideoXBlockTestBase):
    """Test WorkbenchMixin"""

    @patch.object(loader, 'load_scenarios_from_path')
    def test_workbench_scenarios(self, loader_mock):
        loader_mock.return_value = [('Scenario', '<xml/>')]

        self.assertEqual(self.xblock.workbench_scenarios(), [('Scenario', '<xml/>')])
        loader_mock.assert_called_once_with('workbench/scenarios')
