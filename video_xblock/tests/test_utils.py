"""
Test utils.
"""

import unittest
from ddt import ddt, data, unpack

from video_xblock.utils import underscore_to_camelcase


@ddt
class UtilsTest(unittest.TestCase):
    """
    Test Utils.
    """

    @data({
        'test': 'test',
        'test_var': 'testVar',
        'long_test_variable': 'longTestVariable'
    })
    def test_underscore_to_camelcase(self, test_data):
        """Test string conversion from underscore to camelcase"""
        for string, expected_result in test_data.items():
            self.assertEqual(underscore_to_camelcase(string), expected_result)
