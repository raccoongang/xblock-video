# -*- coding: utf-8 -*-
"""
Video XBlock mocks.
"""
import json
from copy import copy
from mock import Mock

from video_xblock.exceptions import VideoXBlockException


class Response(object):
    """
    Dummy Response class.
    """

    def __init__(self, **kwargs):
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
    event_types = []
    event_results = []
    to_return = []

    def __init__(self, **kwargs):
        super(BaseMock, self).__init__()
        if 'mock_magic' in kwargs:
            self.mock = kwargs['mock_magic']

    def expected_value(self, event):
        """
        Should return expected value after mock is applied.
        """
        ret = []
        for item in self.to_return:
            ret.append(self.event_results[event][item])
        return tuple(ret)

    def get_events(self):
        """
        Returns available events.
        """
        return self.event_types


class MockCourse(object):
    """
    Mock Course object with required parameters.
    """

    def __init__(self, course_id):
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
    event_types = ['credentials_created', 'auth_failed']

    event_results = {
        'credentials_created': {
            'client_secret': 'brightcove_client_secret',
            'client_id': 'brightcove_client_id',
            'error_message': ''
        },
        'auth_failed': {
            'client_secret': '',
            'client_id': '',
            'error_message': 'Authentication to Brightcove API failed: no client credentials have been retrieved.'
        }
    }

    def create_credentials(self, event):
        """
        Mock `get_client_credentials` returned value.
        """
        if event == 'auth_failed':
            self.side_effect = VideoXBlockException(self.event_results[event]['error_message'])
        self.return_value = (
            self.event_results[event]['client_secret'],
            self.event_results[event]['client_id'],
            self.event_results[event]['error_message']
        )
        return self

    def expected_value(self, event):
        """
        Return expected value of `authenticate_api` after mock is applied.
        """
        ret = copy(self.event_results[event])
        error = ret.pop('error_message')
        return ret, error


class WistiaAuthMock(BaseMock):
    """
    Wistia auth mock class.
    """
    return_value = Response(status_code=200, body='')

    event_types = ['not_authorized', 'success']

    event_results = {
        'not_authorized': {
            'auth_data': {'token': 'some_token'},
            'error_message': 'Authentication failed.'
        },
        'success': {
            'auth_data': {'token': 'some_token'},
            'error_message': ''
        }
    }

    to_return = ['auth_data', 'error_message']

    def get(self, event):
        """
        Substitute requests.get method.
        """
        if event == 'not_authorized':
            self.return_value = Response(status_code=401)
        return lambda x: self.return_value


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

    event_types = ['status_not_200', 'empty_subs', 'cant_fetch_data', 'success']

    event_results = {
        'status_not_200': {
            'available_languages': [],
            'default_transcripts': [],
            'message': 'No timed transcript may be fetched from a video platform.'
        },
        'empty_subs': {
            'available_languages': _available_languages,
            'default_transcripts': _default_transcripts,
            'message': 'For now, video platform doesn\'t have any timed transcript for this video.'
        },
        'cant_fetch_data': {
            'available_languages': [],
            'default_transcripts': [],
            'message': 'No timed transcript may be fetched from a video platform.'
        },
        'success': {
            'available_languages': _available_languages,
            'default_transcripts': _default_transcripts,
            'message': ''
        }
    }

    to_return = ['default_transcripts', 'message']

    def fetch_default_transcripts_languages(self, event):
        """
        Mock `fetch_default_transcripts_languages` returned value.
        """
        self.return_value = (self.event_results[event]['available_languages'], self.event_results[event]['message'])
        return self


class BrightcoveDefaultTranscriptsMock(BaseMock):
    """
    Brightcove default transcripts mock class.
    """
    _default_transcripts = [
        {'label': u'English', 'lang': u'en',
         'url': None},
        {'label': u'Ukrainian', 'lang': u'uk',
         'url': None}
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

    event_types = ['no_credentials', 'fetch_transcripts_exception', 'no_captions_data', 'success']

    event_results = {
        'no_credentials': {
            'default_transcripts': [],
            'message': 'No API credentials provided'
        },
        'fetch_transcripts_exception': {
            'default_transcripts': [],
            'message': 'No timed transcript may be fetched from a video platform.'
        },
        'no_captions_data': {
            'default_transcripts': [],
            'message': 'For now, video platform doesn\'t have any timed transcript for this video.'
        },
        'success': {
            'default_transcripts': _default_transcripts,
            'message': ''
        }
    }

    to_return = ['default_transcripts', 'message']

    def api_client_get(self, event):
        """
        Mock for `api_client` method.
        """
        if event == 'fetch_transcripts_exception':
            self.side_effect = self.mock()
        elif event == 'no_captions_data':
            self.return_value = Response(status_code=200, body=json.dumps(self._response))
        else:
            ret = copy(self._response)
            ret['text_tracks'] = self.transcripts
            self.return_value = Response(status_code=200, body=json.dumps(ret))
        return self

    def no_credentials(self, event):
        """
        Returns xblock metadata.
        """
        if event == 'no_credentials':
            return {'client_id': '', 'client_secret': ''}
        else:
            return self.mock


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

    event_types = [
        'request_data_exception', 'success_and_data_lang_code',
        'success_and_data_lang_code_exception', 'success_no_data', 'returned_not_found']

    event_results = {
        'request_data_exception': {
            'default_transcripts': [],
            'message': 'No timed transcript may be fetched from a video platform.'
        },
        'success_and_data_lang_code': {
            'default_transcripts': _expected,
            'message': ''
        },
        'success_and_data_lang_code_exception': {
            'default_transcripts': _default_transcripts,
            'message': 'LanguageReverseError'
        },
        'success_no_data': {
            'default_transcripts': [],
            'message': 'For now, video platform doesn\'t have any timed transcript for this video.'
        },
        'returned_not_found': {
            'default_transcripts': [],
            'message': 'doesn\'t exist.'
        }
    }

    to_return = ['default_transcripts', 'message']

    def get(self, event):
        """
        Substitute requests.get method.
        """
        if event == 'request_data_exception':
            self.side_effect = self.mock()
            return self
        elif event == 'success_and_data_lang_code':
            self.return_value = Response(status_code=200, body=json.dumps(self._default_transcripts))
        elif event == 'success_and_data_lang_code_exception':
            default_transcripts = copy(self._default_transcripts)
            default_transcripts[0]['language'] = 'en'
            self.return_value = Response(status_code=200, body=json.dumps(default_transcripts))
        elif event == 'success_no_data':
            self.return_value = Response(status_code=200, body='[]')
        elif event == 'returned_not_found':
            self.return_value = Response(status_code=404, body='{}')
        return lambda x: self.return_value


class YoutubeDownloadTranscriptMock(BaseMock):
    """
    Youtube download default transcript mock class.
    """
    _xml = (
        '<?xml version="1.0" encoding="utf-8" ?><timedtext format="3"><head><pen id="1" fc="#E5E5E5"/>'
        '<pen id="2" fc="#CCCCCC"/><ws id="0"/><ws id="1" mh="2" ju="0" sd="3"/><wp id="0"/>'
        '<wp id="1" ap="6" ah="20" av="100" rc="2" cc="40"/></head><body><w t="0" id="1" wp="1" ws="1"/>'
        '<p t="1560" d="10350" w="1">[Music]</p><p t="4430" d="7480" w="1" a="1"></p>'
        '<p t="4440" d="7470" w="1">[Applause]</p><p t="17090" w="1" a="1"></p><p t="17100" d="6540" w="1">[Music]</p>'
        '<p t="330900" d="3440" w="1" p="2"><s ac="159">like</s></p><p t="337770" w="1" a="1"></p>'
        '<p t="337780" d="3980" w="1">[Music]</p></body></timedtext>'
    )

    event_types = [
        'wrong_arguments', 'no_xml_data', 'success'
    ]

    event_results = {
        'wrong_arguments': {
            'transcript': [],
            'message': '`url` parameter is required.'
        },
        'no_xml_data': {
            'transcript': [],
            'message': 'XMLSyntaxError exception'
        },
        'success': {
            'transcript': 'WEBVTT\n\n\n\n\n\n',
            'message': ''
        }
    }

    to_return = ['transcript', 'message']

    def get(self, event):
        """
        Substitute requests.get method.
        """
        if event == 'no_xml_data':
            self.return_value = Response(status_code=200, body='{}')
        else:
            self.return_value = Response(status_code=200, body=self._xml)
        return lambda x: self.return_value


class BrightcoveDownloadTranscriptMock(BaseMock):
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

    event_types = ['wrong_arguments', 'success', ]

    event_results = {
        'wrong_arguments': {
            'transcript': [],
            'message': '`url` parameter is required.'
        },
        'success': {
            'transcript': _vtt,
            'message': ''
        }
    }

    to_return = ['transcript', 'message']

    def get(self, event):  # pylint: disable=unused-argument
        """
        Substitute requests.get method.
        """
        self.return_value = Response(status_code=200, body=self._vtt)
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

    event_types = ['wrong_arguments', 'success_en', 'success_uk']

    event_results = {
        'wrong_arguments': {
            'transcript': [],
            'message': '`language_code` parameter is required.'
        },
        'success_en': {
            'transcript': 'WEBVTT\n\nhttp://video.google.com/timedtext?lang=en&name=&v=set_video_id_here ',
            'message': ''
        },
        'success_uk': {
            'transcript': 'WEBVTT\n\nhttp://video.google.com/timedtext?lang=uk&name=&v=set_video_id_here ',
            'message': ''
        }
    }

    to_return = ['transcript', 'message']

    def get(self, event):  # pylint: disable=unused-argument
        """
        Substitute player method.
        """
        self.return_value = self._default_transcripts
        return self

    def __iter__(self):
        return iter(self._default_transcripts)
