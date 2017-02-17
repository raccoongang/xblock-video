"""
Backend classes are responsible for video platform specific logic.

E.g. validation, interaction with the platform via API and player rendering to end user.

Base Video player plugin.
"""

import abc
import itertools
import json
import operator
import re

from webob import Response
from xblock.fragment import Fragment
from xblock.plugin import Plugin

from django.conf import settings

from video_xblock.exceptions import VideoXBlockException
from video_xblock.utils import render_resource, resource_string, ugettext as _


class BaseApiClient(object):
    """
    Low level video platform API client.

    Abstracts API interaction details, e.g. requests composition and API credentials handling.

    Subclass your platform specific API client from this base class.
    """

    @abc.abstractmethod
    def get(self, url, headers=None, can_retry=True):
        """
        Issue REST GET request to a given URL.

        Can throw `ApiClientError` or it's subclass.

        Arguments:
            url (str): API url to fetch a resource from.
            headers (dict): Headers necessary as per API, e.g. authorization bearer to perform authorised requests.
            can_retry (bool): True if this is to retry a call if authentication failed.
        Returns:
            Response in python native data format.
        """

    @abc.abstractmethod
    def post(self, url, payload, headers=None, can_retry=True):
        """
        Issue REST POST request to a given URL.

        Can throw ApiClientError or it's subclass.

        Arguments:
            url (str): API url to fetch a resource from.
            payload (dict): POST data.
            headers (dict): Headers necessary as per API, e.g. authorization bearer to perform authorised requests.
            can_retry (bool): True if this is to retry a call if authentication failed.
        Returns:
            Response in python native data format.
        """


class BaseVideoPlayer(Plugin):
    """
    Inherit your video player class from this class.
    """

    __metaclass__ = abc.ABCMeta

    entry_point = 'video_xblock.v1'

    def __init__(self, xblock):
        """
        Initialize base video player class object.
        """
        self.xblock = xblock

    @abc.abstractproperty
    def url_re(self):
        """
        Regex (list) to match video url.

        Can be a regex object, a list of regex objects, or a string.
        """
        return [] or re.compile('') or ''

    @abc.abstractproperty
    def captions_api(self):
        """
        Dictionary of url, request parameters, and response structure of video platform's captions API.
        """
        return {}

    @abc.abstractproperty
    def metadata_fields(self):
        """
        List of keys (str) to be stored in the metadata xblock field.

        To keep xblock metadata field clean on it's each update,
        only backend-specific parameters should be stored in the field.

        Note: this is to add each new key (str) to be stored in metadata to the list being returned here.
        """
        return []

    def get_frag(self, **context):
        """
        Return a Fragment required to render video player on the client side.
        """
        context['player_state'] = json.dumps(context['player_state'])

        frag = Fragment()
        frag.add_css_url(
            'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css'
        )
        css_files = [
            'static/bower_components/video.js/dist/video-js.min.css',
            'static/css/videojs.css',
            'static/css/videojs-contextmenu-ui.css',
        ]
        for css_file in css_files:
            frag.add_css(self.resource_string(css_file))

        frag.add_javascript(
            self.render_resource('static/js/context.js', **context)
        )

        js_files = [
            'static/bower_components/video.js/dist/video.min.js',
            'static/bower_components/videojs-contextmenu/dist/videojs-contextmenu.min.js',
            'static/bower_components/videojs-contextmenu-ui/dist/videojs-contextmenu-ui.min.js',
            'static/js/video-speed.js',
            'static/js/player_state.js',
            'static/js/videojs-speed-handler.js'
        ]

        if json.loads(context['player_state'])['transcripts']:
            js_files += [
                'static/bower_components/videojs-transcript/dist/videojs-transcript.js',
                'static/js/transcript-download.js',
                'static/js/videojs-transcript.js'
            ]

        js_files += [
            'static/js/videojs-tabindex.js',
            'static/js/toggle-button.js',
            'static/js/videojs_event_plugin.js'
        ]

        for js_file in js_files:
            frag.add_javascript(self.resource_string(js_file))

        return frag

    @abc.abstractmethod
    def media_id(self, href):  # pylint: disable=unused-argument
        """
        Extract Platform's media id from the video url.

        E.g. https://example.wistia.com/medias/12345abcde -> 12345abcde
        """
        return ''

    @staticmethod
    @abc.abstractmethod
    def customize_xblock_fields_display(editable_fields):  # pylint: disable=unused-argument
        """
        Customise display of studio editor fields per video platform.

        E.g. 'account_id' should be displayed for Brightcove only.

        Returns:
            client_token_help_message (str): Help message with results of client token generation.
            editable_fields (tuple): All the editable fields to be displayed in studio editor modal.
        """
        return '', ()

    def get_player_html(self, **context):
        """
        Render `self.get_frag` as a html string and returns it as a Response.

        This method is used by `VideoXBlock.render_player()`.

        Rendering sequence is set to JS and must be placed in the head tag,
        and executed before initializing video components.
        """
        frag = self.get_frag(**context)
        return Response(
            self.render_resource('static/html/base.html', frag=frag),
            content_type='text/html'
        )

    def resource_string(self, path):
        """
        Handy helper for getting resources from our kit.
        """
        return resource_string(path)

    def render_resource(self, path, **context):
        """
        Render static resource using provided context.

        Returns:
            django.utils.safestring.SafeText
        """
        return render_resource(path, **context)

    @classmethod
    def match(cls, href):
        """
        Check if provided video `href` can be rendered by a video backend.

        `cls.url_re` attribute, defined in subclassess, is used for the check.
        """
        if isinstance(cls.url_re, list):
            return any(regex.search(href) for regex in cls.url_re)
        elif isinstance(cls.url_re, type(re.compile(''))):
            return cls.url_re.search(href)  # pylint: disable=no-member
        elif isinstance(cls.url_re, basestring):
            return re.search(cls.url_re, href, re.I)

    def add_js_content(self, path, **context):
        """
        Helper for adding javascript code inside <body> section.
        """
        return '<script>' + self.render_resource(path, **context) + '</script>'

    @abc.abstractmethod
    def get_default_transcripts(self, **kwargs):  # pylint: disable=unused-argument
        """
        Fetch transcripts list from a video platform.

        Arguments:
            kwargs (dict): Key-value pairs of API-specific identifiers (account_id, video_id, etc.) and tokens,
                necessary for API calls.
        Returns:
            list: List of dicts of transcripts. Example:
            [
                {
                    'lang': 'en',
                    'label': 'English',
                    'url': 'learning-services-media.brightcove.com/captions/bc_smart_ja.vtt'
                },
                # ...
            ]
            str: Message for a user on default transcripts fetching.
        """
        return [], ''

    @abc.abstractmethod
    def authenticate_api(self, **kwargs):
        """
        Authenticate to a video platform's API in order to perform authorized requests.

        Arguments:
            kwargs (dict): Platform-specific predefined client parameters, required to get credentials / tokens.
        Returns:
            auth_data (dict): Tokens and credentials, necessary to perform authorised API requests.
            error_status_message (str): Message with errors of authentication (if any) for the sake of verbosity.
        """
        return {}, ''

    @abc.abstractmethod
    def download_default_transcript(self, url, language_code):  # pylint: disable=unused-argument
        """
        Download default transcript from a video platform API and format it accordingly to the WebVTT standard.

        Arguments:
            url (str): API url to fetch a default transcript from.
            language_code (str): Language code of a transcript to be downloaded.
        Returns:
            unicode: Transcripts formatted in WebVTT.
        """
        return u''

    @staticmethod
    def get_transcript_language_parameters(lang_code):
        """
        Get parameters of a transcript's language, having checked on consistency with settings.

        Arguments:
            lang_code (str): Raw language code of a transcript, fetched from the video platform.
        Returns:
            lang_code (str): Pre-configured language code, e.g. 'br'
            lang_label (str): Pre-configured language label, e.g. 'Breton'
        """
        # Delete region subtags; reference: https://github.com/edx/edx-platform/blob/master/lms/envs/common.py#L862
        lang_code = lang_code[0:2]
        # Check on consistency with the pre-configured ALL_LANGUAGES
        if lang_code not in [language[0] for language in settings.ALL_LANGUAGES]:
            raise VideoXBlockException(_(
                'Not all the languages of transcripts fetched from video platform are consistent '
                'with the pre-configured ALL_LANGUAGES'
            ))
        lang_label = [language[1] for language in settings.ALL_LANGUAGES if language[0] == lang_code][0]
        return lang_code, lang_label

    @staticmethod
    def clean_default_transcripts(default_transcripts):
        """
        Remove duplicates from default transcripts fetched from a video platform.

        Default transcripts should contain transcripts of distinct languages only.
        Reference:
            http://stackoverflow.com/a/1280464

        Arguments:
            default_transcripts (list): Nested list of dictionaries with data on default transcripts.
        Returns:
            distinct_transcripts (list): Distinct default transcripts to be shown in studio editor.
        """
        get_values = operator.itemgetter('lang')
        default_transcripts.sort(key=get_values)
        distinct_transcripts = []
        for k, g in itertools.groupby(default_transcripts, get_values):
            distinct_transcripts.append(g.next())
        return distinct_transcripts

    def filter_default_transcripts(self, default_transcripts, transcripts):
        """
        Exclude enabled transcripts (fetched from API) from the list of available ones (fetched from video xblock).
        """
        enabled_languages_codes = [t[u'lang'] for t in transcripts]
        default_transcripts = [
            dt for dt in default_transcripts
            if (unicode(dt.get('lang')) not in enabled_languages_codes) and default_transcripts
        ]
        # Default transcripts should contain transcripts of distinct languages only
        distinct_transcripts = self.clean_default_transcripts(default_transcripts)
        return distinct_transcripts
