# -*- coding: utf-8 -*-
"""
Video XBlock mocks.
"""
import json
from copy import copy, deepcopy
from mock import Mock
import requests

from xblock.core import XBlock

from video_xblock.exceptions import VideoXBlockException
from video_xblock.backends import brightcove, youtube, wistia


class ResponseStub(object):
    """
    Dummy ResponseStub class.
    """

    def __init__(self, **kwargs):
        """
        Delegate kwargs to class properties.
        """
        for key, val in kwargs.items():
            setattr(self, key, val)

    @property
    def text(self):
        """
        Make response compatible with requests.Response.
        """
        return getattr(self, 'body', '')

    @property
    def content(self):
        """
        Make response compatible with requests.Response.
        """
        return getattr(self, 'body', '')

    def get(self, key):
        """
        Allow to fetch data from response body by key.
        """
        body = getattr(self, 'body', '')
        if body:
            try:
                return json.loads(body)[key]
            except KeyError:
                pass


class BaseMock(Mock):
    """
    Base custom mock class.
    """

    # `outcomes` should be in the format of dict().items() to keep the order of items.
    # First argument: result name, second argument - dictionary containing result data.
    # Example: (("key1", {}), ("key2", {}), ...)
    outcomes = ()
    to_return = []

    def __init__(self, **kwargs):
        """
        Set specific properties from the kwargs.
        """
        super(BaseMock, self).__init__()
        if 'mock_magic' in kwargs:
            self.mock = kwargs['mock_magic']
        if 'event' in kwargs and kwargs['event'] in self.get_events():
            self.event = kwargs['event']

    @property
    def ordered_results(self):
        """
        Transform `outcomes` to dict.
        """
        return dict(self.outcomes)

    def expected_value(self, event):
        """
        Should return expected value after mock is applied.
        """
        ret = []
        if event in self.get_events():
            for item in self.to_return:
                ret.append(self.ordered_results[event][item])
        return tuple(ret)

    def get_events(self):
        """
        Return available events.
        """
        ret = []
        for key, val in self.outcomes:
            if isinstance(key, str) and isinstance(val, dict):
                ret.append(key)
        return ret

    @staticmethod
    def apply_mock(event, *args):
        """
        Save state of object before mocks are applied.
        """
        pass


class MockCourse(object):
    """
    Mock Course object with required parameters.
    """

    def __init__(self, course_id):
        """
        Delegate course_id to class property and set course's language.

        """
        self.course_id = course_id
        self.language = 'en'


class YoutubeAuthMock(BaseMock):
    """
    Youtube auth mock class.
    """

    pass


class VimeoAuthMock(BaseMock):
    """
    Vimeo auth mock class.
    """

    pass


class BrightcoveAuthMock(BaseMock):
    """
    Brightcove auth mock class.
    """

    outcomes = (
        (
            'credentials_created',
            {
                'client_secret': 'brightcove_client_secret',
                'client_id': 'brightcove_client_id',
                'error_message': ''
            }
        ),
        (
            'auth_failed',
            {
                'client_secret': '',
                'client_id': '',
                'error_message': 'Authentication to Brightcove API failed: no client credentials have been retrieved.'
            }
        )
    )

    def create_credentials(self):
        """
        Mock `get_client_credentials` returned value.
        """
        if self.event == 'auth_failed':
            self.side_effect = VideoXBlockException(self.ordered_results[self.event]['error_message'])
        self.return_value = (
            self.ordered_results[self.event]['client_secret'],
            self.ordered_results[self.event]['client_id'],
            self.ordered_results[self.event]['error_message']
        )
        return self

    def expected_value(self, event):
        """
        Return expected value of `authenticate_api` after mock is applied.
        """
        ret = copy(self.ordered_results[event])
        error = ret.pop('error_message')
        return ret, error

    @staticmethod
    def apply_mock(event):
        """
        Save state of auth related entities before mocks are applied.
        """
        brightcove.BrightcoveApiClient.create_credentials = BrightcoveAuthMock(event=event).create_credentials()
        return {
            'obj': brightcove.BrightcoveApiClient,
            'attrs': ['create_credentials', ],
            'value': [brightcove.BrightcoveApiClient.create_credentials, ]
        }


class WistiaAuthMock(BaseMock):
    """
    Wistia auth mock class.
    """

    return_value = ResponseStub(status_code=200, body='')

    outcomes = (
        (
            'not_authorized',
            {'auth_data': {'token': 'some_token'}, 'error_message': 'Authentication failed.'}
        ),
        (
            'success',
            {'auth_data': {'token': 'some_token'}, 'error_message': ''}
        )
    )

    to_return = ['auth_data', 'error_message']

    def get(self):
        """
        Substitute requests.get method.
        """
        if self.event == 'not_authorized':
            self.return_value = ResponseStub(status_code=401)
        return lambda x: self.return_value

    @staticmethod
    def apply_mock(event):
        """
        Save state of auth related entities before mocks are applied.
        """
        return {
            'obj': requests,
            'attrs': ['get', ],
            'value': [deepcopy(requests.get), ]
        }


class YoutubeDefaultTranscriptsMock(BaseMock):
    """
    Youtube default transcripts mock class.
    """

    _available_languages = [
        (u'en', u'English', u''),
        (u'uk', u'Українська', u'')
    ]

    _default_transcripts = [
        {'label': u'English', 'lang': u'en',
         'url': 'http://video.google.com/timedtext?lang=en&name=&v=set_video_id_here'},
        {'label': u'Ukrainian', 'lang': u'uk',
         'url': 'http://video.google.com/timedtext?lang=uk&name=&v=set_video_id_here'}
    ]

    outcomes = (
        (
            'status_not_200',
            {
                'available_languages': [],
                'default_transcripts': [],
                'message': 'No timed transcript may be fetched from a video platform.'
            }
        ),
        (
            'empty_subs',
            {
                'available_languages': _available_languages,
                'default_transcripts': _default_transcripts,
                'message': 'For now, video platform doesn\'t have any timed transcript for this video.'
            }
        ),
        (
            'cant_fetch_data',
            {
                'available_languages': [],
                'default_transcripts': [],
                'message': 'No timed transcript may be fetched from a video platform.'
            }
        ),
        (
            'success',
            {
                'available_languages': _available_languages,
                'default_transcripts': _default_transcripts,
                'message': ''
            }
        )
    )

    to_return = ['default_transcripts', 'message']

    def fetch_default_transcripts_languages(self):
        """
        Mock `fetch_default_transcripts_languages` returned value.
        """
        self.return_value = (
            self.ordered_results[self.event]['available_languages'], self.ordered_results[self.event]['message']
        )
        return self

    @staticmethod
    @XBlock.register_temp_plugin(youtube.YoutubePlayer, 'youtube')
    def apply_mock(event):
        """
        Save state of default transcripts related entities before mocks are applied.
        """
        player = XBlock.load_class('youtube')
        player.fetch_default_transcripts_languages = YoutubeDefaultTranscriptsMock(event=event) \
            .fetch_default_transcripts_languages()
        return {
            'obj': player,
            'attrs': ['fetch_default_transcripts_languages'],
            'value': [player.fetch_default_transcripts_languages, ]
        }


class BrightcoveDefaultTranscriptsMock(BaseMock):
    """
    Brightcove default transcripts mock class.
    """

    _default_transcripts = [
        {'label': u'English', 'lang': u'en', 'url': None},
        {'label': u'Ukrainian', 'lang': u'uk', 'url': None}
    ]

    _response = {
        "master": {
            "url": "http://host/master.mp4"
        },
        "poster": {
            "url": "http://learning-services-media.brightcove.com/images/for_video/Water-In-Motion-poster.png",
            "width": 640,
            "height": 360
        },
        "thumbnail": {
            "url": "http://learning-services-media.brightcove.com/images/for_video/Water-In-Motion-thumbnail.png",
            "width": 160,
            "height": 90
        },
        "capture-images": False,
        "callbacks": ["http://solutions.brightcove.com/bcls/di-api/di-callbacks.php"]
    }

    transcripts = [
        {
            "url": "http://learning-services-media.brightcove.com/captions/for_video/Water-in-Motion.vtt",
            "srclang": "en",
            "kind": "captions",
            "label": "EN",
            "default": True
        },
        {
            "url": "http://learning-services-media.brightcove.com/captions/for_video/Water-in-Motion.vtt",
            "srclang": "uk",
            "kind": "captions",
            "label": "UK",
            "default": False
        }
    ]

    outcomes = (
        (
            'no_credentials',
            {
                'default_transcripts': [],
                'message': 'No API credentials provided'
            }
        ),
        (
            'fetch_transcripts_exception',
            {
                'default_transcripts': [],
                'message': 'No timed transcript may be fetched from a video platform.'
            }
        ),
        (
            'no_captions_data',
            {
                'default_transcripts': [],
                'message': 'For now, video platform doesn\'t have any timed transcript for this video.'
            }
        ),
        (
            'success',
            {
                'default_transcripts': _default_transcripts,
                'message': ''
            }
        )
    )

    to_return = ['default_transcripts', 'message']

    def api_client_get(self):
        """
        Mock for `api_client` method.
        """
        if self.event == 'fetch_transcripts_exception':
            self.side_effect = self.mock()
        elif self.event == 'no_captions_data':
            self.return_value = ResponseStub(status_code=200, body=json.dumps(self._response))
        else:
            ret = copy(self._response)
            ret['text_tracks'] = self.transcripts
            self.return_value = ResponseStub(status_code=200, body=json.dumps(ret))
        return self

    def no_credentials(self):
        """
        Return xblock metadata.
        """
        if self.event == 'no_credentials':
            return {'client_id': '', 'client_secret': ''}
        else:
            return self.mock

    @staticmethod
    def apply_mock(event):
        """
        Save state of default transcripts related entities before mocks are applied.
        """
        brightcove.BrightcoveApiClient.get = BrightcoveDefaultTranscriptsMock(
            mock_magic=brightcove.BrightcoveApiClientError, event=event
        ).api_client_get()
        return {
            'obj': brightcove.BrightcoveApiClient,
            'attrs': ['get', ],
            'value': [deepcopy(brightcove.BrightcoveApiClient.get), ]
        }


class WistiaDefaultTranscriptsMock(BaseMock):
    """
    Wistia default transcripts mock class.
    """

    _expected = [
        {
            'lang': u'en',
            'url': 'url_can_not_be_generated',
            'text': u'http://video.google.com/timedtext?lang=en&name=&v=set_video_id_here',
            'label': u'English'
        },
        {
            'lang': u'uk',
            'url': 'url_can_not_be_generated',
            'text': u'http://video.google.com/timedtext?lang=uk&name=&v=set_video_id_here',
            'label': u'Ukrainian'
        }
    ]

    _default_transcripts = [
        {'english_name': u'English', 'language': u'eng',
         'text': 'http://video.google.com/timedtext?lang=en&name=&v=set_video_id_here'},
        {'english_name': u'Ukrainian', 'language': u'ukr',
         'text': 'http://video.google.com/timedtext?lang=uk&name=&v=set_video_id_here'}
    ]

    outcomes = (
        (
            'request_data_exception',
            {
                'default_transcripts': [],
                'message': 'No timed transcript may be fetched from a video platform.'
            }
        ),
        (
            'success_and_data_lang_code',
            {
                'default_transcripts': _expected,
                'message': ''
            }
        ),
        (
            'success_and_data_lang_code_exception',
            {
                'default_transcripts': _default_transcripts,
                'message': 'LanguageReverseError'
            }
        ),
        (
            'success_no_data',
            {
                'default_transcripts': [],
                'message': 'For now, video platform doesn\'t have any timed transcript for this video.'
            }
        ),
        (
            'returned_not_found',
            {
                'default_transcripts': [],
                'message': 'doesn\'t exist.'
            }
        )
    )

    to_return = ['default_transcripts', 'message']

    def get(self):
        """
        Substitute requests.get method.
        """
        if self.event == 'request_data_exception':
            self.side_effect = self.mock()
            return self
        else:
            default_transcripts = copy(self._default_transcripts)
            default_transcripts[0]['language'] = 'en'
            return_value_by_event = {
                'success_and_data_lang_code_exception': {
                    'status_code': 200,
                    'body': json.dumps(default_transcripts)
                },
                'success_and_data_lang_code': {
                    'status_code': 200,
                    'body': json.dumps(self._default_transcripts)
                },
                'success_no_data': {
                    'status_code': 200,
                    'body': '{}'
                },
                'returned_not_found': {
                    'status_code': 404,
                    'body': '{}'
                },
            }
            self.return_value = ResponseStub(**return_value_by_event[self.event])
        return lambda x: self.return_value

    @staticmethod
    def apply_mock(event):
        """
        Save state of default transcripts related entities before mocks are applied.
        """
        requests.get = WistiaDefaultTranscriptsMock(
            mock_magic=requests.exceptions.RequestException, event=event
        ).get()
        return {
            'obj': requests,
            'attrs': ['get', ],
            'value': [deepcopy(requests.get), ]
        }


class VimeoDefaultTranscriptsMock(BaseMock):
    """
    Temporary mock for vimeo player. Need to be updated.
    """

    outcomes = [('get_transcripts', [])]

    to_return = [[], '']


class BaseDownloadTranscriptMock(BaseMock):
    """
    Base download transcript mock class.
    """

    @staticmethod
    def apply_mock(event):
        """
        Save state of download transcript related entities before mocks are applied.
        """
        requests.get = YoutubeDownloadTranscriptMock(event=event).get()
        return {
            'obj': requests,
            'attrs': ['get', ],
            'value': [deepcopy(requests.get), ]
        }


class YoutubeDownloadTranscriptMock(BaseDownloadTranscriptMock):
    """
    Youtube download default transcript mock class.
    """

    _vtt = u"""WEBVTT

1
00:00:00.000 --> 00:00:01.679
[INTRODUZIONE]

2
00:00:03.093 --> 00:00:06.392
Oggi voglio parlare di sottotitoli, di nuovo.

3
00:00:06.400 --> 00:00:10.811
Come sapete, io sono una grande sostenitrice dei sottotitoli su YouTube.

4
00:00:10.812 --> 00:00:13.290
Forse me la canto e me la suono da sola un po',

"""

    _xml = (
        '<?xml version="1.0" encoding="utf-8" ?><transcript><text start="0" dur="1.68">[INTRODUZIONE]</text>'
        '<text start="3.093" dur="3.3">Oggi voglio parlare di\nsottotitoli, di nuovo.</text>'
        '<text start="6.4" dur="4.412">Come sapete, io sono una grande\nsostenitrice dei sottotitoli su YouTube.</text>'
        '<text start="10.812" dur="2.479">Forse me la canto e me la suono da sola un po&amp;#39;,</text></transcript>'
    )

    outcomes = (
        ('wrong_arguments', {'transcript': [], 'message': '`url` parameter is required.'}),
        ('no_xml_data', {'transcript': [], 'message': 'XMLSyntaxError exception'}),
        ('success', {'transcript': _vtt, 'message': ''})
    )

    to_return = ['transcript', 'message']

    def get(self):
        """
        Substitute requests.get method.
        """
        if self.event == 'no_xml_data':
            self.return_value = ResponseStub(status_code=200, body='{}')
        else:
            self.return_value = ResponseStub(status_code=200, body=self._xml)
        return lambda x: self.return_value


class BrightcoveDownloadTranscriptMock(BaseDownloadTranscriptMock):
    """
    Brightcove download default transcript mock class.
    """

    _vtt = """WEBVTT

00:06.047 --> 00:06.068
Hi.

00:06.070 --> 00:08.041
I'm Bob Bailey, a Learning Specialist with Brightcove.

00:09.041 --> 00:11.003
In this video, we'll learn about Brightcove Smart Players

00:21.052 --> 00:23.027
the next few years.

00:25.042 --> 00:27.094
accessed from mobile devices."""

    outcomes = (
        ('wrong_arguments', {'transcript': [], 'message': '`url` parameter is required.'}),
        ('success', {'transcript': _vtt, 'message': ''})
    )

    to_return = ['transcript', 'message']

    def get(self):
        """
        Substitute requests.get method.
        """
        self.return_value = ResponseStub(status_code=200, body=self._vtt)
        return lambda x: self.return_value


class WistiaDownloadTranscriptMock(BaseMock):
    """
    Brightcove download default transcript mock class.
    """

    _default_transcripts = [
        {
            'lang': u'en',
            'url': 'url_can_not_be_generated',
            'text': u'http://video.google.com/timedtext?lang=en&name=&v=set_video_id_here',
            'label': u'English'
        },
        {
            'lang': u'uk',
            'url': 'url_can_not_be_generated',
            'text': u'http://video.google.com/timedtext?lang=uk&name=&v=set_video_id_here',
            'label': u'Ukrainian'
        }
    ]

    outcomes = (
        (
            'wrong_arguments',
            {
                'transcript': [],
                'message': '`language_code` parameter is required.'
            }
        ),
        (
            'success_en',
            {
                'transcript': 'WEBVTT\n\nhttp://video.google.com/timedtext?lang=en&name=&v=set_video_id_here ',
                'message': ''
            }
        ),
        (
            'success_uk',
            {
                'transcript': 'WEBVTT\n\nhttp://video.google.com/timedtext?lang=uk&name=&v=set_video_id_here ',
                'message': ''
            }
        )
    )

    to_return = ['transcript', 'message']

    def get(self):
        """
        Substitute player method.
        """
        self.return_value = self._default_transcripts
        return self

    def __iter__(self):
        """
        Iter through default transcripts.
        """
        return iter(self._default_transcripts)

    @staticmethod
    @XBlock.register_temp_plugin(wistia.WistiaPlayer, 'wistia')
    def apply_mock(event):
        """
        Save state of download transcript related entities before mocks are applied.
        """
        player = XBlock.load_class('wistia')
        player.default_transcripts = WistiaDownloadTranscriptMock(event=event).get()
        return {
            'obj': player,
            'attrs': ['default_transcripts', ],
            'value': [deepcopy(player.default_transcripts), ]
        }


class VimeoDownloadTranscriptMock(BaseMock):
    """
    Temporary vimeo download transcript mock object.
    """

    outcomes = [('success', '')]
    to_return = ('', '')
