"""
YouTube Video player plugin
"""

import json
import re
import urllib
import requests
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
    metadata_fields = []

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

    # Stores default transcripts fetched from the Youtube captions API
    default_transcripts = []

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
            "controls": True,
            "preload": 'auto',
            "plugins": {
                "xblockEventPlugin": {},
                "offset": {
                    "start": context['start_time'],
                    "end": context['end_time'],
                    "current_time": context['player_state']['current_time'],
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
            list: List of pairs of codes and labels of captions' languages fetched from API,
                together with transcripts' names if any.
                If the transcript name is not empty on youtube server we have to pass
                name param in url in order to get transcript.
                Example: http://video.google.com/timedtext?lang=en&v={video_id}&name={transcript_name}
                Reference: https://git.io/vMoCA
        """
        utf8_parser = etree.XMLParser(encoding='utf-8')
        # This is to update self.captions_api with a video id.
        self.captions_api['params']['v'] = video_id
        transcripts_param = {'type': 'list', 'v': self.captions_api['params']['v']}
        available_languages = []
        message = ''

        try:
            data = requests.get('http://' + self.captions_api['url'], params=transcripts_param)
        except requests.exceptions.RequestException as exception:
            # Probably, current API has changed
            message = 'No timed transcript may be fetched from a video platform. ' \
                      'Error: {}'.format(str(exception))
            return available_languages, message

        if data.status_code == 200 and data.text:
            youtube_data = etree.fromstring(data.content, parser=utf8_parser)
            empty_subs = False if [el.get('transcript_list') for el in youtube_data] else True
            available_languages = [
                [el.get('lang_code'), el.get('lang_translated'), el.get('name')]
                for el in youtube_data if el.tag == 'track'
            ]
            if empty_subs:
                message = 'For now, video platform doesn\'t have any timed transcript for this video.'
        else:
            message = 'No timed transcript may be fetched from a video platform.'

        return available_languages, message

    def get_default_transcripts(self, **kwargs):
        """
        Fetches transcripts list from a video platform.
        """
        # Fetch available transcripts' languages from API
        video_id = kwargs.get('video_id')
        available_languages, message = self.fetch_default_transcripts_languages(video_id)

        default_transcripts = []
        for lang_code, lang_translated, transcript_name in available_languages:  # pylint: disable=unused-variable
            self.captions_api['params']['lang'] = lang_code
            self.captions_api['params']['name'] = transcript_name
            transcript_url = 'http://{url}?{params}'.format(
                url=self.captions_api['url'],
                params=urllib.urlencode(self.captions_api['params'])
            )
            # Update default transcripts languages parameters in accordance with pre-configured language settings
            lang_code, lang_label = self.get_transcript_language_parameters(lang_code)
            default_transcript = {
                'lang': lang_code,
                'label': lang_label,
                'url': transcript_url,
            }
            default_transcripts.append(default_transcript)
        self.default_transcripts = default_transcripts
        return default_transcripts, message

    @staticmethod
    def convert_sec_to_caption_format(sec):
        """
        Converts seconds to the timestamp of the format `hh:mm:ss:mss`, e.g. 00:00:03.887

        """
        mins, secs = divmod(sec, 60)  # pylint: disable=unused-variable
        hours, mins = divmod(mins, 60)

        hours_formatted = str(int(hours)).zfill(2)
        mins_formatted = str(int(mins)).zfill(2)
        # TODO: handle a case of secs with 3 and more digits, e.g. `00:01:100.765 --> 00:01:104.322`
        secs_formatted = str("{:.3f}".format(round(sec, 3))).zfill(6)

        timing = "{}:{}:{}".format(
            hours_formatted,
            mins_formatted,
            secs_formatted
        )

        return timing

    def download_default_transcript(self, url, language_code=None):
        """
        Downloads default transcript from Youtube API and convert to WebVTT-like unicode.

        References:
            https://git.io/vMK6W
            https://git.io/vMoEc

        """
        utf8_parser = etree.XMLParser(encoding='utf-8')
        data = requests.get(url)
        sub = u"\nWEBVTT\n\n"
        sub_starts, sub_ends, sub_texts = [], [], []
        xmltree = etree.fromstring(data.content, parser=utf8_parser)

        for element in xmltree:
            if element.tag == "text":
                start = float(element.get("start"))
                duration = float(element.get("dur", 0))  # dur is not mandatory
                text = element.text
                end = start + duration
                if text:
                    start = self.convert_sec_to_caption_format(start)
                    sub_starts.append(start)
                    end = self.convert_sec_to_caption_format(end)
                    sub_ends.append(end)
                    sub_texts.append(text.replace('\n', ' '))

        sub_dict = {'start': sub_starts, 'end': sub_ends, 'text': sub_texts}
        for i, el in enumerate(sub_dict['text'], 1):  # pylint: disable=unused-variable
            start = sub_dict['start'][i-1]
            end = sub_dict['end'][i-1]
            timing = '{} --> {}'.format(start, end)
            text = sub_dict['text'][i-1]
            sub_element = unicode(i) + u'\n' + unicode(timing) + u'\n' + unicode(text) + u'\n\n'
            sub += sub_element
        return sub

    def dispatch(self, request, suffix):
        pass
