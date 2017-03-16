"""
Video XBlock mixins geared toward specific subsets of functionality.
"""

import json
import requests

from pycaption import detect_format, WebVTTWriter
from webob import Response

from xblock.fields import Scope, Boolean, Float, String
from xblock.core import XBlock

from xmodule.contentstore.django import contentstore
from xmodule.contentstore.content import StaticContent

from .utils import ugettext as _


@XBlock.wants('contentstore')
class ContentStoreMixin(XBlock):
    """
    Proxy to future `contentstore` service.

    If `contentstore` service is not provided by `runtime` it returns classes
    from `xmodule.contentstore`
    """

    @property
    def contentstore(self):
        """
        Proxy to `xmodule.contentstore.contentstore` class.
        """
        contentstore_service = self.runtime.service(self, 'contentstore')
        if contentstore_service:
            return contentstore_service.contentstore
        return contentstore

    @property
    def static_content(self):
        """
        Proxy to `xmodule.contentstore.StaticContent` class.
        """
        contentstore_service = self.runtime.service(self, 'contentstore')
        if contentstore_service:
            return contentstore_service.StaticContent
        return StaticContent


class TranscriptsMixin(XBlock):
    """
    TranscriptsMixin class to encapsulate transcripts-related logic.
    """

    @staticmethod
    def convert_caps_to_vtt(caps):
        """
        Utility method to convert any supported transcripts into WebVTT format.

        Supported input formats: DFXP/TTML - SAMI - SCC - SRT - WebVTT.

        Arguments:
            caps (unicode): Raw transcripts.
        Returns:
            unicode: Transcripts converted into WebVTT format.
        """
        reader = detect_format(caps)
        if reader:
            return WebVTTWriter().write(reader().read(caps))
        else:
            return u''

    def route_transcripts(self, transcripts):
        """
        Re-route non .vtt transcripts to `str_to_vtt` handler.

        Arguments:
            transcripts (unicode): Raw transcripts.
        """
        transcripts = json.loads(transcripts) if transcripts else []
        for tran in transcripts:
            if not tran['url'].endswith('.vtt'):
                tran['url'] = self.runtime.handler_url(
                    self, 'srt_to_vtt', query=tran['url']
                )
            yield tran

    def get_transcript_download_link(self):
        """
        Return link for downloading of a transcript of the current captions' language (if a transcript exists).
        """
        transcripts = json.loads(self.transcripts) if self.transcripts else []
        for transcript in transcripts:
            if transcript.get('lang') == self.captions_language:
                return transcript.get('url')
        return ''

    def create_transcript_file(self, ext='.vtt', trans_str='', reference_name=''):
        """
        Upload a transcript, fetched from a video platform's API, to video xblock.

        Arguments:
            ext (str): format of transcript file, default is vtt.
            trans_str (str): multiple string for convert to vtt file.
            reference_name (str): name of transcript file.
        Returns:
            File's file_name and external_url.
        """
        # Define location of default transcript as a future asset and prepare content to store in assets
        file_name = reference_name.replace(" ", "_") + ext
        course_key = self.location.course_key  # pylint: disable=no-member
        content_loc = self.static_content.compute_location(course_key, file_name)  # AssetLocator object
        content = self.static_content(
            content_loc,
            file_name,
            'application/json',
            trans_str.encode('UTF-8')
        )  # StaticContent object
        external_url = '/' + str(content_loc)

        # Commit the content
        self.contentstore().save(content)

        return file_name, external_url

    def convert_3playmedia_caps_to_vtt(self, caps, video_id, lang="en", lang_label="English"):
        """
        Utility method to convert any supported transcripts into WebVTT format.

        Arguments:
            caps (unicode)  : Raw transcripts.
            video_id (str)  : Video id from player.
            lang (str)      : Iso code for language.
            lang_label (str): Name of language.
        Returns:
            response (dict) : {"lang": lang, "url": url, "label": lang_label}
                lang (str)  : Iso code for language.
                url (str)   : External url for vtt file.
                label (str) : Name of language.
        """
        out, response = [], {}
        for item in caps.splitlines():
            if item == '':
                item = ' \n'
            elif '-->' in item:
                # This line is deltatime stamp 00:05:55.030 --> 00:05:57.200.
                # Length this line is 29 characters.
                item = item[:29]
            out.append(item)

        caps = u'\n'.join(out).replace('\n&nbsp;', '')
        sub = self.convert_caps_to_vtt(caps=caps)
        reference_name = "{lang_label}_captions_video_{video_id}".format(
            lang_label=lang_label, video_id=video_id
        ).encode('utf8')
        file_name, external_url = self.create_transcript_file(
            trans_str=sub, reference_name=reference_name
        )
        if file_name:
            response = {"lang": lang, "url": external_url, "label": lang_label}
        return response

    def get_translations_from_3playmedia(self, file_id, apikey):
        """
        Method to fetched from 3playmedia translations for file_id.

        Arguments:
            file_id (str) : File id on 3playmedia.
            apikey (str)  : Authentication key on 3playmedia.
        Returns:
            response (tuple)    : status, translations or status, error_message
            status (str)        : Status response error or success.
            translations (list) : List of translations (dict) .
            error_message (dict): Description of error.
        """
        domain = 'https://static.3playmedia.com/'
        transcripts_3playmedia = requests.get(
            '{domain}files/{file_id}/translations?apikey={api_key}'.format(
                domain=domain, file_id=file_id, api_key=apikey
            )
        ).json()
        errors = isinstance(transcripts_3playmedia, dict) and transcripts_3playmedia.get('errors')
        if errors:
            return 'error', {'error_message': u'\n'.join(errors.values())}

        translations = []
        for transcript in transcripts_3playmedia:
            tid = transcript.get('id', '')
            sub_unicode = requests.get(
                '{domain}files/{file_id}/translations/{tid}/captions.vtt?apikey={api_key}'.format(
                    domain=domain, file_id=file_id, api_key=apikey, tid=tid
                )
            ).text
            translations.append(
                self.convert_3playmedia_caps_to_vtt(
                    caps=sub_unicode,
                    video_id=self.get_player().media_id(self.href),
                    lang=transcript.get('target_language_iso_639_1_code', ''),
                    lang_label=transcript.get('target_language_name', '')
                )
            )
        return 'success', translations

    @XBlock.json_handler
    def get_transcripts_3playmedia_api_handler(self, data, _suffix=''):
        """
        Xblock handler to authenticate to a video platform's API. Called by JavaScript of `studio_view`.

        Arguments:
            data (dict): Data from frontend, necessary for authentication (tokens, account id, etc).
            suffix (str): Slug used for routing.
        Returns:
            response (dict): Status messages key-value pairs.
        """
        apikey = data.get('api_key', self.threeplaymedia_apikey) or ''
        file_id = data.get('file_id', '')
        status, _transcripts = self.get_translations_from_3playmedia(
            apikey=apikey, file_id=file_id
        )
        if status == 'error':
            return _transcripts

        transcript_original = requests.get(
            'https://static.3playmedia.com/files/{file_id}/transcript.vtt?apikey={api_key}'.format(
                file_id=file_id, api_key=apikey
            )
        ).text
        _transcripts.append(
            self.convert_3playmedia_caps_to_vtt(
                caps=transcript_original,
                video_id=self.get_player().media_id(self.href)
            )
        )
        return {
            'transcripts': _transcripts,
            'success_message': _(
                'Successfully fetched transcripts from 3playMedia. Please check transcripts list above.'
            )
        }

    @XBlock.handler
    def download_transcript(self, request, _suffix=''):
        """
        Download a transcript.

        Arguments:
            request (webob.Request): Request to handle.
            suffix (string): Slug used for routing.
        Returns:
            File with the correct name.
        """
        trans_path = self.get_path_for(request.query_string)
        result = requests.get(request.host_url + request.query_string).text
        filename = self.get_file_name_from_path(trans_path)
        response = Response(result)
        headerlist = [
            ('Content-Type', 'text/plain'),
            ('Content-Disposition', 'attachment; filename={}'.format(filename))
        ]
        response.headerlist = headerlist
        return response

    @XBlock.handler
    def srt_to_vtt(self, request, _suffix=''):
        """
        Fetch raw transcripts, convert them into WebVTT format and return back.

        Path to raw transcripts is passed in as `request.query_string`.

        Arguments:
            request (webob.Request): The request to handle
            suffix (string): The remainder of the url, after the handler url prefix, if available.
        Returns:
            webob.Response: WebVTT transcripts wrapped in Response object.
        """
        caps_path = request.query_string
        caps = requests.get(request.host_url + caps_path).text
        return Response(self.convert_caps_to_vtt(caps))


class PlaybackStateMixin(XBlock):
    """
    PlaybackStateMixin encapsulates video-playback related data.

    These fields are not visible to end-user.
    """

    current_time = Float(
        default=0,
        scope=Scope.user_state,
        help='Seconds played back after the start'
    )

    playback_rate = Float(
        default=1,
        scope=Scope.preferences,
        help='Supported video playbacks speeds are: 0.5, 1, 1.5, 2'
    )

    volume = Float(
        default=1,
        scope=Scope.preferences,
        help='Video volume: from 0 to 1'
    )

    muted = Boolean(
        default=False,
        scope=Scope.preferences,
        help="Video is muted or not"
    )

    captions_language = String(
        default='',
        scope=Scope.preferences,
        help="ISO code for the current language for captions and transcripts"
    )

    transcripts = String(
        default='',
        scope=Scope.content,
        display_name=_('Upload transcript'),
        help=_(
            'Add transcripts in different languages. Click below to specify a language and upload an .srt transcript'
            ' file for that language.'
        )
    )

    transcripts_enabled = Boolean(
        default=False,
        scope=Scope.preferences,
        help="Transcripts are enabled or not"
    )

    captions_enabled = Boolean(
        default=False,
        scope=Scope.preferences,
        help="Captions are enabled or not"
    )

    @property
    def player_state(self):
        """
        Return video player state as a dictionary.
        """
        course = self.runtime.modulestore.get_course(self.course_id)
        transcripts = json.loads(self.transcripts) if self.transcripts else []
        transcripts_object = {
            trans['lang']: {'url': trans['url'], 'label': trans['label']}
            for trans in transcripts
        }
        return {
            'current_time': self.current_time,
            'muted': self.muted,
            'playback_rate': self.playback_rate,
            'volume': self.volume,
            'transcripts': transcripts,
            'transcripts_enabled': self.transcripts_enabled,
            'captions_enabled': self.captions_enabled,
            'captions_language': self.captions_language or course.language,
            'transcripts_object': transcripts_object
        }

    @player_state.setter
    def player_state(self, state):
        """
        Save video player state passed in as a dict into xblock's fields.

        Arguments:
            state (dict): Video player state key-value pairs.
        """
        self.current_time = state.get('current_time', self.current_time)
        self.muted = state.get('muted', self.muted)
        self.playback_rate = state.get('playback_rate', self.playback_rate)
        self.volume = state.get('volume', self.volume)
        self.transcripts = state.get('transcripts', self.transcripts)
        self.transcripts_enabled = state.get('transcripts_enabled', self.transcripts_enabled)
        self.captions_enabled = state.get('captions_enabled', self.captions_enabled)
        self.captions_language = state.get('captions_language', self.captions_language)
