"""
Video XBlock mocks.
"""
import json
from mock import Mock


class Response(object):
    """
    Dummy Response class.
    """
    def __init__(self, **kwargs):
        for key, val in kwargs.items():
            setattr(self, key, val)


class BaseMock(Mock):
    """
    Base custom mock class.
    """
    @staticmethod
    def expected_value(**kwargs):
        """
        Should return expected value after mock is applied.
        """
        raise NotImplementedError


class MockCourse(object):
    """
    Mock Course object with required parameters.
    """
    def __init__(self, course_id):
        self.course_id = course_id
        self.language = 'en'


class YoutubeAuthMock(Mock):
    """
    Youtube auth mock class.
    """
    return_value = {}


class BrightcoveAuthMock(BaseMock):
    """
    Brightcove auth mock class.
    """
    def get_client_credentials(self):
        """
        Mock `get_client_credentials` returned value.
        """
        client_secret = 'brightcove_client_secret'
        client_id = 'brightcove_client_id'
        error_message = ""
        self.return_value = (client_secret, client_id, error_message)
        return self

    def get_access_token(self):
        """
        Mock `get_access_token` returned value.
        """
        access_token = 'brightcove_access_token'
        error_message = ''
        self.return_value = (access_token, error_message)
        return self

    @staticmethod
    def expected_value(**kwargs):
        """
        Return expected value of `authenticate_api` after mock is applied.
        """
        return {
            'access_token': 'brightcove_access_token',
            'client_id': 'brightcove_client_id',
            'client_secret': 'brightcove_client_secret'
        }


class WistiaAuthMock(BaseMock):
    """
    Wistia auth mock class.
    """
    return_value = Response(status_code=200, body=json.dumps([
        {
            "id": 24050105,
            "name": "Free HD Stock Video - Small bird dances and sings on branch (see descr for HQ download)-SD",
            "type": "Video",
            "created": "2016-12-15T17:55:05+00:00",
            "updated": "2016-12-15T17:59:52+00:00",
            "duration": 20.235,
            "hashed_id": "jzmku8z83i",
            "description": "",
            "progress": 1,
            "status": "ready",
            "thumbnail": {
                "url": "https://embed-ssl.wistia.com/deliveries/ff3286178bab78d086f817c943490f009148fd30.jpg?"
                       "image_crop_resized=200x120",
                "width": 200,
                "height": 120
            },
            "project": {
                "id": 2721534,
                "name": "Olena's First Project",
                "hashed_id": "4yx77uhfz2"
            },
            "assets": [
                {
                    "url": "http://embed.wistia.com/deliveries/6b9f6db40df41cb40330d2997257f3e8ba6463b4.bin",
                    "width": 640,
                    "height": 360,
                    "fileSize": 1821697,
                    "contentType": "video/mp4",
                    "type": "OriginalFile"
                },
                {
                    "url": "http://embed.wistia.com/deliveries/f6d29793d1c1b97ec6e0e559ac33d1b7080a17fa.bin",
                    "width": 640,
                    "height": 360,
                    "fileSize": 823508,
                    "contentType": "video/mp4",
                    "type": "IphoneVideoFile"
                },
                {
                    "url": "http://embed.wistia.com/deliveries/73020e9aa8fb2e77985a64aba24ce6138fadf10a.bin",
                    "width": 640,
                    "height": 360,
                    "fileSize": 733,
                    "contentType": "application/x-mpegURL",
                    "type": "HlsVideoFile"
                },
                {
                    "url": "http://embed.wistia.com/deliveries/f14af0034f154e6830157969dbaa46af4c621253.bin",
                    "width": 640,
                    "height": 360,
                    "fileSize": 831067,
                    "contentType": "video/x-flv",
                    "type": "FlashVideoFile"
                },
                {
                    "url": "http://embed.wistia.com/deliveries/87bdbf18e1046c13c70aeb5cee098afb34f87987.bin",
                    "width": 400,
                    "height": 224,
                    "fileSize": 543924,
                    "contentType": "video/mp4",
                    "type": "Mp4VideoFile"
                },
                {
                    "url": "http://embed.wistia.com/deliveries/497014caa0969de26c927678bfec21611f6f02e2.bin",
                    "width": 400,
                    "height": 224,
                    "fileSize": 727,
                    "contentType": "application/x-mpegURL",
                    "type": "HlsVideoFile"
                },
                {
                    "url": "http://embed.wistia.com/deliveries/ff3286178bab78d086f817c943490f009148fd30.bin",
                    "width": 640,
                    "height": 360,
                    "fileSize": 35797,
                    "contentType": "image/jpeg",
                    "type": "StillImageFile"
                },
                {
                    "url": "http://embed.wistia.com/deliveries/42927e69f02eb4aaf8716044bc6dcfe16e1b0b94.bin",
                    "width": 2000,
                    "height": 560,
                    "fileSize": 227332,
                    "contentType": "image/jpeg",
                    "type": "StoryboardFile"
                }
            ],
            "embedCode": "",
        },
        {
            "id": 24052595,
            "name": "videoplayback",
            "type": "Video",
            "created": "2016-12-15T19:54:06+00:00",
            "updated": "2016-12-15T20:05:32+00:00",
            "duration": 226.408,
            "hashed_id": "r3houattxx",
            "description": "",
            "progress": 1,
            "status": "ready",
            "thumbnail": {
                "url": "https://embed-ssl.wistia.com/deliveries/b58e5072395ea71796670b9712fea78bd8008394.jpg?"
                       "image_crop_resized=200x120",
                "width": 200,
                "height": 120
            },
            "project": {
                "id": 2721830,
                "name": "black",
                "hashed_id": "3n5xvdhj27"
            },
            "assets": [
                {
                    "url": "http://embed.wistia.com/deliveries/96977e34a938543c9e70d257f4e9e904afa65bed.bin",
                    "width": 640,
                    "height": 360,
                    "fileSize": 18836441,
                    "contentType": "video/mp4",
                    "type": "OriginalFile"
                },
                {
                    "url": "http://embed.wistia.com/deliveries/166b9275abb1fd350403af02d90d8c8a09b06064.bin",
                    "width": 640,
                    "height": 360,
                    "fileSize": 17917880,
                    "contentType": "video/mp4",
                    "type": "IphoneVideoFile"
                },
                {
                    "url": "http://embed.wistia.com/deliveries/6b90940f9d5744826356f176039eeef8f0bb64f5.bin",
                    "width": 640,
                    "height": 360,
                    "fileSize": 7350,
                    "contentType": "application/x-mpegURL",
                    "type": "HlsVideoFile"
                },
                {
                    "url": "http://embed.wistia.com/deliveries/989923ee8fe5e587c02b79ab65486652b34201ca.bin",
                    "width": 640,
                    "height": 360,
                    "fileSize": 18030462,
                    "contentType": "video/x-flv",
                    "type": "FlashVideoFile"
                },
                {
                    "url": "http://embed.wistia.com/deliveries/4d147cb6baa52adb928707b74641c1c25e40eafc.bin",
                    "width": 400,
                    "height": 224,
                    "fileSize": 9794362,
                    "contentType": "video/mp4",
                    "type": "Mp4VideoFile"
                },
                {
                    "url": "http://embed.wistia.com/deliveries/bd4245e059e12c5f6786e5c5c84c10658b34d0e0.bin",
                    "width": 400,
                    "height": 224,
                    "fileSize": 7317,
                    "contentType": "application/x-mpegURL",
                    "type": "HlsVideoFile"
                },
                {
                    "url": "http://embed.wistia.com/deliveries/b58e5072395ea71796670b9712fea78bd8008394.bin",
                    "width": 640,
                    "height": 360,
                    "fileSize": 43784,
                    "contentType": "image/jpeg",
                    "type": "StillImageFile"
                },
                {
                    "url": "http://embed.wistia.com/deliveries/5870582f8927cd41e0a0784237381c01d185ca98.bin",
                    "width": 2000,
                    "height": 2352,
                    "fileSize": 1033715,
                    "contentType": "image/jpeg",
                    "type": "StoryboardFile"
                }
            ],
            "embedCode": ""
        }
    ]))

    @staticmethod
    def expected_value(**kwargs):
        """
        Return expected value of `authenticate_api` after mock is applied.
        """
        return {'token': kwargs.get('token', '')}
