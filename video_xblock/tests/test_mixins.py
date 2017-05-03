import unittest
from mock import patch, Mock, PropertyMock

from video_xblock import VideoXBlock
from video_xblock.mixins import LocationMixin
from video_xblock.tests.base import VideoXBlockTestBase


class LocationMixinTests(VideoXBlockTestBase):
    """Test LocationMixin"""

    def test_no_location_block_id(self):
        self.assertFalse(hasattr(self.xblock,'location'))
        self.assertEqual(self.xblock.block_id, 'block_id')

    def test_no_location_course_key(self):
        self.assertFalse(hasattr(self.xblock,'location'))
        self.assertEqual(self.xblock.course_key, 'course_key')

    def test_no_location_deprecated_string(self):
        self.assertFalse(hasattr(self.xblock,'location'))
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
