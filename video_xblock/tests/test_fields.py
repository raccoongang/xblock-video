"""Tests for classes defined in fields.py."""

import datetime
import unittest

from video_xblock.fields import RelativeTime


class RelativeTimeTest(unittest.TestCase):
    """
    Test RelativeTime field.
    """
    delta = RelativeTime()

    def test_from_json(self):
        self.assertEqual(
            RelativeTimeTest.delta.from_json('0:05:07'),
            datetime.timedelta(seconds=307)
        )

        self.assertEqual(
            RelativeTimeTest.delta.from_json(100.0),
            datetime.timedelta(seconds=100)
        )
        self.assertEqual(
            RelativeTimeTest.delta.from_json(None),
            datetime.timedelta(seconds=0)
        )

        with self.assertRaises(TypeError):
            RelativeTimeTest.delta.from_json(1234)  # int

        with self.assertRaises(ValueError):
            RelativeTimeTest.delta.from_json("77:77:77")

    def test_enforce_type(self):
        self.assertEqual(RelativeTimeTest.delta.enforce_type(None), None)
        self.assertEqual(
            RelativeTimeTest.delta.enforce_type(datetime.timedelta(days=1, seconds=46799)),
            datetime.timedelta(days=1, seconds=46799)
        )
        self.assertEqual(
            RelativeTimeTest.delta.enforce_type('0:05:07'),
            datetime.timedelta(seconds=307)
        )
        with self.assertRaises(TypeError):
            RelativeTimeTest.delta.enforce_type([1])

    def test_to_json(self):
        self.assertEqual(
            "01:02:03",
            RelativeTimeTest.delta.to_json(datetime.timedelta(seconds=3723))
        )
        self.assertEqual(
            "00:00:00",
            RelativeTimeTest.delta.to_json(None)
        )
        self.assertEqual(
            "00:01:40",
            RelativeTimeTest.delta.to_json(100.0)
        )

        error_msg = "RelativeTime max value is 23:59:59=86400.0 seconds, but 90000.0 seconds is passed"
        with self.assertRaisesRegexp(ValueError, error_msg):
            RelativeTimeTest.delta.to_json(datetime.timedelta(seconds=90000))

        with self.assertRaises(TypeError):
            RelativeTimeTest.delta.to_json("123")

    def test_str(self):
        self.assertEqual(
            "01:02:03",
            RelativeTimeTest.delta.to_json(datetime.timedelta(seconds=3723))
        )
        self.assertEqual(
            "11:02:03",
            RelativeTimeTest.delta.to_json(datetime.timedelta(seconds=39723))
        )
