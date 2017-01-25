"""
Brightcove Video player plugin
"""

import re
import base64
import json
import requests

from xblock.fragment import Fragment

from video_xblock import BaseVideoPlayer


class BrightcovePlayer(BaseVideoPlayer):
    """
    BrightcovePlayer is used for videos hosted on the Brightcove Video Cloud.
    """

    url_re = re.compile(r'https:\/\/studio.brightcove.com\/products\/videocloud\/media\/videos\/(?P<media_id>\d+)')

    # Current api for requesting transcripts.
    # For example: https://cms.api.brightcove.com/v1/accounts/{account_id}/videos/{video_ID}
    # Docs on captions: https://docs.brightcove.com/en/video-cloud/cms-api/guides/webvtt.html
    # Docs on auth: https://docs.brightcove.com/en/video-cloud/oauth-api/getting-started/oauth-api-overview.html
    captions_api = {
        'url': 'cms.api.brightcove.com/v1/accounts/{account_id}/videos/{media_id}',
        'authorised_request_header': {
            'Authorization': 'Bearer {access_token}'
        },
        'response': {
            'language_code': 'srclang',  # no language_label translated in English may be fetched from API
            'subs': 'src'  # e.g., "http://learning-services-media.brightcove.com/captions/bc_smart_ja.vtt"
        }
    }

    def media_id(self, href):
        """
        Brightcove specific implementation of BaseVideoPlayer.media_id()
        """
        return self.url_re.match(href).group('media_id')

    def get_frag(self, **context):
        """
        Compose an XBlock fragment with video player to be rendered in student view.

        Brightcove backend is a special case and doesn't use vanila Video.js player.
        Because of this it doesn't use `super.get_frag()`
        """

        frag = Fragment(
            self.render_resource('../static/html/brightcove.html', **context)
        )
        frag.add_css_url(
            'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css'
        )
        frag.add_content(
            self.add_js_content('../static/js/player_state.js', **context)
        )
        frag.add_content(
            self.add_js_content('../static/js/toggle-button.js')
        )
        if context['player_state']['transcripts']:
            frag.add_content(
                self.add_js_content('../static/bower_components/videojs-transcript/dist/videojs-transcript.js')
            )
            frag.add_content(
                self.add_js_content('../static/js/videojs-transcript.js', **context)
            )
        frag.add_content(
            self.add_js_content('../static/js/videojs-tabindex.js', **context)
        )
        frag.add_content(
            self.add_js_content('../static/js/videojs_event_plugin.js', **context)
        )
        frag.add_content(
            self.add_js_content('../static/bower_components/videojs-offset/dist/videojs-offset.js')
        )
        frag.add_content(
            self.add_js_content('../static/js/videojs-speed-handler.js', **context)
        )
        frag.add_content(
            self.add_js_content('../static/js/brightcove-videojs-init.js', **context)
        )
        frag.add_css(
            self.resource_string('../static/css/brightcove.css')
        )
        return frag

    @staticmethod
    def get_client_credentials(token, account_id):
        """
        Gets client credentials, given a client token and an account_id.
        Reference: https://docs.brightcove.com/en/video-cloud/oauth-api/guides/get-client-credentials.html

        """
        headers = {'Authorization': 'BC_TOKEN {}'.format(token)}
        # TODO implement application name (optional): --data 'name=videoxblock&maximum_scope=...'
        data = [{
            "identity": {
                "type": "video-cloud-account",
                "account-id": account_id
            },
            "operations": [
                "video-cloud/video/update"
            ]
        }]
        payload = {'maximum_scope': json.dumps(data)}
        url = 'https://oauth.brightcove.com/v4/client_credentials'
        response = requests.post(url, data=payload, headers=headers)
        response_data = json.loads(unicode(response.content))

        if response.status_code == 201 and response.text:
            client_secret = response_data.get('client_secret')
            client_id = response_data.get('client_id')
            error_message = ''
        else:
            error_message = "Authentication failed: no client credentials have been retrieved. " \
                            "Response: {}".format(response.text)
            client_secret, client_id = '', ''

        return client_secret, client_id, error_message

    @staticmethod
    def get_access_token(client_id, client_secret):
        """
        Gets access token from a Brightcove API to perform authorized requests.
        Reference: https://docs.brightcove.com/en/video-cloud/oauth-api/guides/get-token.html

        """
        # Authorization header: the entire {client_id}:{client_secret} string must be Base64-encoded
        client_credentials_encoded = base64.b64encode('{client_id}:{client_secret}'.format(
            client_id=client_id,
            client_secret=client_secret))
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization': 'Basic {}'.format(client_credentials_encoded)
        }
        data = {'grant_type': 'client_credentials'}
        url = 'https://oauth.brightcove.com/v3/access_token'
        response = requests.post(url, data=data, headers=headers)
        response_data = json.loads(unicode(response.content))

        if response.status_code == 200 and response.text:
            access_token = response_data.get('access_token')
            error_message = ''
        else:
            access_token = ''
            error_message = "Authentication failed: no access token has been fetched. " \
                            "Response: {}".format(response.text)

        return access_token, error_message

    def authenticate_api(self, **kwargs):
        """
        Authenticates to a Brightcove API in order to perform authorized requests.

        Arguments:
            kwargs (dict): token and account_id key-value pairs.
        Returns:
            access token (str), and
            error_status_message (str) for verbosity.
        """
        # TODO implement validation in JS (kwargs)
        token, account_id = kwargs['token'], kwargs['account_id']
        client_secret, client_id, error_message = self.get_client_credentials(token, account_id)
        error_status_message = ''
        if error_message:
            error_status_message = error_message
        access_token, error_message = self.get_access_token(client_id, client_secret)
        if error_message:
            error_status_message = error_message
        return access_token, error_status_message
