"""
VideoXBlock mixins test cases.
"""

from mock import patch, Mock, PropertyMock

from video_xblock.tests.base import VideoXBlockTestBase
from video_xblock.utils import loader


class ContentStoreMixinTest(VideoXBlockTestBase):
    """Test ContentStoreMixin"""

    @patch('video_xblock.video_xblock.import_module')
    def test_import_from(self, import_module_mock):
        import_module_mock.return_value = module_mock = Mock()
        type(module_mock).test_class = PropertyMock(return_value='a_class')

        self.assertEqual(self.xblock.import_from('test_module', 'test_class'), 'a_class')
        import_module_mock.assert_called_once_with('test_module')

    def test_contentstore_no_service(self):
        with patch.object(self.xblock, 'import_from') as import_mock:
            import_mock.return_value = 'contentstore_test'

            self.assertEqual(self.xblock.contentstore, 'contentstore_test')
            import_mock.assert_called_once_with('xmodule.contentstore.django', 'contentstore')

    def test_static_content_no_service(self):
        with patch.object(self.xblock, 'import_from') as import_mock:
            import_mock.return_value = 'StaticContent_test'

            self.assertEqual(self.xblock.static_content, 'StaticContent_test')
            import_mock.assert_called_once_with('xmodule.contentstore.content', 'StaticContent')

    def test_contentstore(self):
        with patch.object(self.xblock, 'runtime') as runtime_mock:
            service_mock = runtime_mock.service
            type(service_mock.return_value).contentstore = PropertyMock(return_value='contentstore_test')

            self.assertEqual(self.xblock.contentstore, 'contentstore_test')
            service_mock.assert_called_once_with(self.xblock, 'contentstore')

    def test_static_content(self):
        with patch.object(self.xblock, 'runtime') as runtime_mock:
            service_mock = runtime_mock.service
            type(service_mock.return_value).StaticContent = PropertyMock(return_value='StaticContent_test')

            self.assertEqual(self.xblock.static_content, 'StaticContent_test')
            service_mock.assert_called_once_with(self.xblock, 'contentstore')


class LocationMixinTests(VideoXBlockTestBase):
    """Test LocationMixin"""

    def test_no_location_block_id(self):
        self.assertFalse(hasattr(self.xblock, 'location'))
        self.assertEqual(self.xblock.block_id, 'block_id')

    def test_no_location_course_key(self):
        self.assertFalse(hasattr(self.xblock, 'location'))
        self.assertEqual(self.xblock.course_key, 'course_key')

    def test_no_location_deprecated_string(self):
        self.assertFalse(hasattr(self.xblock, 'location'))
        self.assertEqual(self.xblock.deprecated_string, 'deprecated_string')

    def test_block_id(self):
        self.xblock.location = location_mock = Mock()
        type(location_mock).block_id = block_mock = PropertyMock(return_value='test_block_id')

        self.assertEqual(self.xblock.block_id, 'test_block_id')
        block_mock.assert_called_once()

    def test_course_key(self):
        self.xblock.location = location_mock = Mock()
        type(location_mock).course_key = course_key_mock = PropertyMock(return_value='test_course_key')

        self.assertEqual(self.xblock.course_key, 'test_course_key')
        course_key_mock.assert_called_once()

    def test_deprecated_string(self):
        self.xblock.location = location_mock = Mock()
        location_mock.to_deprecated_string = str_mock = Mock(return_value='test_str')

        self.assertEqual(self.xblock.deprecated_string, 'test_str')
        str_mock.assert_called_once()


class PlaybackStateMixinTests(VideoXBlockTestBase):
    """Test PlaybackStateMixin"""

    def test_fallback_course_default_language(self):
        with patch.object(self.xblock, 'runtime') as runtime_mock:
            runtime_mock.service = service_mock = Mock(return_value=None)
            self.assertEqual(self.xblock.course_default_language, 'en')
            service_mock.assert_called_once()

    def test_course_default_language(self):
        with patch.object(self.xblock, 'runtime') as runtime_mock:
            service_mock = runtime_mock.service
            lang_mock = type(runtime_mock.modulestore.get_course.return_value).language = PropertyMock(return_value='test_lang')
            lang_mock.return_value = 'test_lang'
            self.xblock.course_id = course_id_mock = PropertyMock()

            self.assertEqual(self.xblock.course_default_language, 'test_lang')
            service_mock.assert_called_once_with(self.xblock, 'modulestore')
            lang_mock.assert_called_once()


class WorkbenchMixinTest(VideoXBlockTestBase):
    """Test WorkbenchMixin"""

    @patch.object(loader, 'load_scenarios_from_path')
    def test_workbench_scenarios(self, loader_mock):
        loader_mock.return_value = [('Scenario', '<xml/>')]

        self.assertEqual(self.xblock.workbench_scenarios(), [('Scenario', '<xml/>')])
        loader_mock.assert_called_once_with('workbench/scenarios')
