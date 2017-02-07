# -*- coding: utf-8 -*-
"""
Video XBlock mocks.
"""
import json
from copy import copy
from mock import Mock


class Response(object):
    """
    Dummy Response class.
    """

    def __init__(self, **kwargs):
        for key, val in kwargs.items():
            setattr(self, key, val)

    @property
    def text(self):
        return getattr(self, 'body', '')


class BaseMock(Mock):
    """
    Base custom mock class.
    """
    event_types = []

    def expected_value(self, **kwargs):
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

    def expected_value(self, **kwargs):
        """
        Return expected value of `authenticate_api` after mock is applied.
        """
        return self.return_value


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

    def expected_value(self, **kwargs):
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
    return_value = Response(status_code=200, body='')

    def expected_value(self, **kwargs):
        """
        Return expected value of `authenticate_api` after mock is applied.
        """
        return {'token': kwargs.get('token', '')}


class YoutubeDefaultTranscriptsMock(BaseMock):
    event_types = ['status_not_200', 'empty_subs', 'cant_fetch_data', 'success']

    available_languages = [
        (u'en', u'English', u''),
        (u'uk', u'Українська', u'')
    ]

    default_transcripts = [
        {'label': u'English', 'lang': u'en',
         'url': 'http://video.google.com/timedtext?lang=en&name=&v=set_video_id_here'},
        {'label': u'Ukrainian', 'lang': u'uk',
         'url': 'http://video.google.com/timedtext?lang=uk&name=&v=set_video_id_here'}
    ]

    event_results = {
        'status_not_200': {
            'available_languages': [],
            'default_transcripts': [],
            'message': 'No timed transcript may be fetched from a video platform.'
        },
        'empty_subs': {
            'available_languages': available_languages,
            'default_transcripts': default_transcripts,
            'message': 'For now, video platform doesn\'t have any timed transcript for this video.'
        },
        'cant_fetch_data': {
            'available_languages': [],
            'default_transcripts': [],
            'message': 'No timed transcript may be fetched from a video platform.'
        },
        'success': {
            'available_languages': available_languages,
            'default_transcripts': default_transcripts,
            'message': ''
        }
    }

    def fetch_default_transcripts_languages(self, event):
        """
        Mock `fetch_default_transcripts_languages` returned value.
        """
        self.return_value = (self.event_results[event]['available_languages'], self.event_results[event]['message'])
        return self

    def expected_value(self, **kwargs):
        """
        Return expected value of `get_default_transcripts` after mock is applied.
        """
        event = kwargs.get('event', '')
        return self.event_results[event]['default_transcripts'], self.event_results[event]['message']


class BrightcoveDefaultTranscriptsMock(BaseMock):
    event_types = [
        'fetch_transcripts_exception', 'text_tracks_not_in_response',
        'response_not_authorized', 'status_not_200', 'success'
    ]

    default_transcripts = [
        {'label': u'English', 'lang': u'en',
         'url': None},
        {'label': u'Ukrainian', 'lang': u'uk',
         'url': None}
    ]

    response = {
        "master": {
            "url": "http://host/master.mp4"
        },
        "poster": {
            "url":"http://learning-services-media.brightcove.com/images/for_video/Water-In-Motion-poster.png",
            "width": 640,
            "height": 360
        },
        "thumbnail": {
            "url": "http://learning-services-media.brightcove.com/images/for_video/Water-In-Motion-thumbnail.png",
            "width": 160,
            "height": 90
        },
        "capture-images": False,
        "text_tracks": [],
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

    event_results = {
        'fetch_transcripts_exception': {
            'default_transcripts': [],
            'message': 'No timed transcript may be fetched from a video platform.',
            'response': ''
        },
        'text_tracks_not_in_response': {
            'default_transcripts': default_transcripts,
            'message': 'For now, video platform doesn\'t have any timed transcript for this video.',
            'response': Response(status_code=200, body=json.dumps(response))
        },
        'response_not_authorized': {
            'default_transcripts': [],
            'message': '',
            'response': Response(status_code=401, body='[{"error_code":"UNAUTHORIZED","message":"Permission denied."}]')
        },
        'status_not_200': {
            'default_transcripts': [],
            'message': 'No timed transcript may be fetched from a video platform.',
            'response': Response(status_code=500, body='[{"error_code":"SERVER_ERROR","message":"Server Error."}]')
        },
        'success': {
            'default_transcripts': default_transcripts,
            'message': 'No timed transcript may be fetched from a video platform.',
            'response': ''
        }
    }

    def __init__(self, event=None):
        super(BrightcoveDefaultTranscriptsMock, self).__init__()
        if not event:
            event = 'success'
        if event == 'fetch_transcripts_exception':
            from requests.exceptions import RequestException
            self.side_effect = RequestException()
        elif event == 'success':
            ret = copy(self.response)
            ret['text_tracks'] = self.transcripts
            self.return_value = Response(status_code=200, body=json.dumps(ret))
        else:
            self.return_value = self.event_results[event]['response']

    def expected_value(self, **kwargs):
        """
        Return expected value of `get_default_transcripts` after mock is applied.
        """
        event = kwargs.get('event', '')
        return self.event_results[event]['default_transcripts'], self.event_results[event]['message']
