"""
YouTube Video player plugin
"""

import json
import re
import requests
import urllib
from lxml import etree

from video_xblock import BaseVideoPlayer


class YoutubePlayer(BaseVideoPlayer):
    """
    YoutubePlayer is used for videos hosted on the Youtube.com
    """

    # Regex is taken from http://regexr.com/3a2p0
    url_re = re.compile(
        r'(?:youtube\.com\/\S*(?:(?:\/e(?:mbed))?\/|watch\?(?:\S*?&?v\=))|youtu\.be\/)(?P<media_id>[a-zA-Z0-9_-]{6,11})'
    )

    # YouTube API for requesting transcripts.
    # For example: http://video.google.com/timedtext?lang=en&v=QLQ-85Td2Gs
    captions_api = {
        'url': 'video.google.com/timedtext',
        'params': {
            'v': 'set_video_id_here',
            'lang': 'en',  # not mandatory
            'name': ''     # not mandatory
        },
        'response': {
            'language_code': 'lang_code',
            'language_label': 'lang_translated',
            'subs': 'text'
        }
    }

    def media_id(self, href):
        return self.url_re.search(href).group('media_id')

    def get_frag(self, **context):
        context['data_setup'] = json.dumps({
            "controlBar": {
                "volumeMenuButton": {
                    "inline": False,
                    "vertical": True
                }
            },
            "techOrder": ["youtube"],
            "sources": [{
                "type": "video/youtube",
                "src": context['url']
            }],
            "youtube": {"iv_load_policy": 1},
            "playbackRates": [0.5, 1.0, 1.5, 2.0],
            "plugins": {
                "xblockEventPlugin": {},
                "offset": {
                    "start": context['start_time'],
                    "end": context['end_time']
                },
                "videoJSSpeedHandler": {},
            }
        })

        frag = super(YoutubePlayer, self).get_frag(**context)
        frag.add_content(
            self.render_resource('../static/html/youtube.html', **context)
        )

        frag.add_javascript(self.resource_string(
            '../static/bower_components/videojs-youtube/dist/Youtube.min.js'
        ))

        frag.add_javascript(self.resource_string(
            '../static/bower_components/videojs-offset/dist/videojs-offset.min.js'
        ))

        return frag

    @staticmethod
    def customize_xblock_fields_display(editable_fields):
        """
        Customises display of studio editor fields per a video platform.
        Authentication to API is not required for Youtube.
        """
        message = 'This field is to be disabled.'
        editable_fields = list(editable_fields)
        editable_fields.remove('account_id')
        editable_fields.remove('player_id')
        editable_fields.remove('token')
        customised_editable_fields = tuple(editable_fields)
        return message, customised_editable_fields

    def authenticate_api(self, **kwargs):
        """
        Current Youtube captions API doesn't require authentication, but this may change.
        """
        return {}, ''

    def fetch_default_transcripts_languages(self, video_id):
        """
        Fetches available transcripts languages from a Youtube server.

        Arguments:
            video_id (str): media id fetched from href field of studio-edit modal.
        Returns:
            list: List of pairs of codes and labels of captions' languages fetched from API.
        """
        utf8_parser = etree.XMLParser(encoding='utf-8')
        # This is to update self.captions_api with a video id.
        self.captions_api['params']['v'] = video_id
        transcripts_param = {'type': 'list', 'v': self.captions_api['params']['v']}
        data = requests.get('http://' + self.captions_api['url'], params=transcripts_param)

        if data.status_code == 200 and data.text:
            youtube_data = etree.fromstring(data.content, parser=utf8_parser)
            available_languages = [
                [el.get('lang_code'), el.get('lang_translated')]
                for el in youtube_data if el.tag == 'track'
            ]
            return available_languages

        return []

    def fetch_default_transcripts_names(self):
        """
        Fetches available transcripts' names from a Youtube server.

        If the transcript name is not empty on youtube server we have to pass
        name param in url in order to get transcript.
        Example: http://video.google.com/timedtext?lang=en&v={video_id}&name={transcript_name}

        Reference: https://git.io/vMoCA
        """
        utf8_parser = etree.XMLParser(encoding='utf-8')
        transcripts_param = {'type': 'list', 'v': self.captions_api['params']['v']}

        data = requests.get('http://' + self.captions_api['url'], params=transcripts_param)

        if data.status_code == 200 and data.text:
            data = etree.fromstring(data.content, parser=utf8_parser)
            transcripts_names = [
                el.get('name')
                for el in data if el.tag == 'track'
            ]
            return transcripts_names

        return []

    def get_default_transcripts(self, **kwargs):
        """
        Fetches transcripts list from a video platform.
        """
        # Fetch available transcripts' languages from API
        video_id = kwargs.get('video_id')
        available_languages = self.fetch_default_transcripts_languages(video_id)

        # Get transcript name if any
        transcripts_names = self.fetch_default_transcripts_names()

        default_transcripts = []
        for i, lang_available in enumerate(available_languages):
            transcript_name = transcripts_names[i]
            lang_code = lang_available[0]
            self.captions_api['params']['lang'] = lang_code
            self.captions_api['params']['name'] = transcript_name
            transcript_url = 'http://{url}?{params}'.format(
                url=self.captions_api['url'],
                params=urllib.urlencode(self.captions_api['params'])
            )
            lang_code, lang_label = self.get_transcript_language_parameters(lang_code)
            default_transcript = {
                'lang': lang_code,
                'label': lang_label,
                'url': transcript_url,
            }
            default_transcripts.append(default_transcript)

        return default_transcripts

    def download_default_transcript(self, url):  # pylint: disable=unused-argument
        # TODO: implement
        return []
