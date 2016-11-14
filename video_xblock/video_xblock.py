"""
Video XBlock provides a convenient way to embed videos hosted on
supported platforms into your course.
All you need to provide is video url, this XBlock does the rest for you.
"""

import abc
import logging
import pkg_resources
import re

from HTMLParser import HTMLParser
from webob import Response
from xblock.core import XBlock
from xblock.fields import Scope, String
from xblock.fragment import Fragment
from xblock.plugin import Plugin
from xblock.validation import ValidationMessage
from xblockutils.studio_editable import StudioEditableXBlockMixin

from django.template import Template, Context


html_parser = HTMLParser()

_ = lambda text: text
log = logging.getLogger(__name__)

# From official Wistia documentation. May change in the future
# https://wistia.com/doc/construct-an-embed-code#the_regex
VIDEO_URL_RE = re.compile(r'https?:\/\/(.+)?(wistia.com|wi.st)\/(medias|embed)\/.*')


class BaseVideoPlayer(Plugin):
    __metaclass__ = abc.ABCMeta

    entry_point = 'video_xblock.v1'

    @abc.abstractproperty
    def url_re(self):
        """
        Regex (list) to match video url
        """
        return [] or re.compile('') or ''

    @abc.abstractmethod
    def get_frag(self, **context):
        """
        Returns a Fragment required to render video player on the client side.
        """
        return Fragment('<video />')

    @abc.abstractmethod
    def media_id(self, href):
        """
        Extracts Platform's media id from the video url.
        E.g. https://example.wistia.com/medias/12345abcde -> 12345abcde
        """

        return ''

    def get_player_html(self, **context):
        """
        Renders self.get_frag as a html string and returns it as a Response.
        This method is used by VideoXBlock.render_player()
        """
        frag = self.get_frag(**context)
        return Response(
            frag.head_html() + frag.body_html() + frag.foot_html(),
            content_type='text/html'
        )

    def resource_string(self, path):
        """Handy helper for getting resources from our kit."""
        data = pkg_resources.resource_string(__name__, path)
        return data.decode("utf8")


    @classmethod
    def match(cls, href):
        if isinstance(cls.url_re, list):
            return any(regex.search(href) for regex in cls.url_re)
        elif isinstance(cls.url_re, type(re.compile(''))):
            return cls.url_re.search(href)
        elif isinstance(cls.url_re, basestring):
            return re.search(cls.url_re, href, re.I)


class DummyPlayer(BaseVideoPlayer):
    """
    DummyPlayer is used as a placeholder for those cases when appropriate
    player cannot be displayed.
    """
    url_re = re.compile(r'')

    def get_frag(self, **context):
        return Fragment(u'[Here be Video]')

    def media_id(self, href):
        return '<media_id>'


class YoutubePlayer(BaseVideoPlayer):
    """
    YoutubePlayer is used for videos hosted on the Youtube.com
    """

    # http://regexr.com/3a2p0
    url_re = re.compile(r'(?:youtube\.com\/\S*(?:(?:\/e(?:mbed))?\/|watch\?(?:\S*?&?v\=))|youtu\.be\/)(?P<media_id>[a-zA-Z0-9_-]{6,11})')

    def media_id(self, href):
        return self.url_re.search(href).group('media_id')

    def get_frag(self, **context):
        html = Template(self.resource_string("static/html/youtube.html"))
        frag = Fragment(
            html_parser.unescape(
                html.render(Context(context))
            )
        )

        frag.add_css(self.resource_string(
            'static/bower_components/video.js/dist/video-js.min.css'
        ))
        frag.add_javascript(self.resource_string(
            'static/bower_components/video.js/dist/video.min.js'
        ))
        # frag.add_javascript(self.resource_string(
        #     'static/video-speed.js'
        # ))
        frag.add_javascript(self.resource_string(
            'static/bower_components/videojs-youtube/dist/Youtube.min.js'
        ))

        return frag


class BrightcovePlayer(BaseVideoPlayer):
    """
    BrightcovePlayer is used for videos hosted on the Brightcove Video Cloud
    """

    url_re = re.compile(r'https:\/\/studio.brightcove.com\/products\/videocloud\/media\/videos\/(?P<media_id>\d+)')

    def media_id(self, href):
        return self.url_re.match(href).group('media_id')

    def get_frag(self, **context):
        html = Template(self.resource_string("static/html/brightcove.html"))
        frag = Fragment(
            html_parser.unescape(
                html.render(Context(context))
            )
        )
        return frag


class WistiaPlayer(BaseVideoPlayer):
    """
    WistiaPlayer is used for videos hosted on the Wistia Video Cloud
    """

    url_re = re.compile(r'https?:\/\/(.+)?(wistia.com|wi.st)\/(medias|embed)\/(?P<media_id>.*)')

    def media_id(self, href):
        return self.url_re.search(href).group('media_id')

    def get_frag(self, **context):
        html = Template(self.resource_string("static/html/wistiavideo.html"))
        frag = Fragment(
            html_parser.unescape(
                html.render(Context(context))
            )
        )
        frag.add_css(self.resource_string(
            'static/bower_components/video.js/dist/video-js.min.css'
        ))
        frag.add_javascript(self.resource_string(
            'static/bower_components/video.js/dist/video.min.js'
        ))
        frag.add_javascript(self.resource_string(
            'static/videojs-wistia/src/wistia.js'
        ))

        return frag


class VideoXBlock(StudioEditableXBlockMixin, XBlock):
    """
    Main VideoXBlock class.
    Responsible for saving video settings and rendering it for students.
    """

    icon_class = "video"

    display_name = String(
        default='Video',
        display_name=_('Component Display Name'),
        help=_('The name students see. This name appears in the course ribbon and as a header for the video.'),
        scope=Scope.content,
    )

    href = String(
        default='',
        display_name=_('Video URL'),
        help=_('URL of the video page. E.g. https://example.wistia.com/medias/12345abcde'),
        scope=Scope.content
    )

    account_id = String(
        default='',
        display_name=_('Account Id'),
        help=_('Your Brightcove account id'),
        scope=Scope.content,
    )

    player_name = String(
        default='dummy-player',
        scope=Scope.content
    )

    editable_fields = ('display_name', 'href', 'account_id')

    def validate_field_data(self, validation, data):
        """
        Validate data submitted via xblock edit pop-up
        """

        if data.href == '':
            return
        for player_name, player_class in BaseVideoPlayer.load_classes():
            if player_class.match(data.href):
                return

        validation.add(ValidationMessage(
            ValidationMessage.ERROR,
            _(u"Incorrect or unsupported video URL, please recheck.")
        ))

    def resource_string(self, path):
        """Handy helper for getting resources from our kit."""
        data = pkg_resources.resource_string(__name__, path)
        return data.decode("utf8")

    def student_view(self, context=None):
        """
        The primary view of the VideoXBlock, shown to students
        when viewing courses.
        """

        player_url = self.runtime.handler_url(self, 'render_player')
        html = Template(self.resource_string('static/html/student_view.html'))
        frag = Fragment(
            html_parser.unescape(
                html.render(Context({'player_url': player_url}))
            )
        )
        return frag

    @XBlock.handler
    def render_player(self, request, suffix=''):
        """
        student_view() loads this handler as an iframe to display actual
        video player.
        """
        player = self.get_player()
        return player.get_player_html(
            url=self.href, autoplay=False, account_id=self.account_id,
            video_id=player.media_id(self.href))

    def clean_studio_edits(self, data):
        data['player_name'] = 'dummy-player'  # XXX: use field's default
        for player_name, player_class in BaseVideoPlayer.load_classes():
            if player_name == 'dummy-player':
                continue
            if player_class.match(data['href']):
                data['player_name'] = player_name

    def get_player(self):
        player = BaseVideoPlayer.load_class(self.player_name)
        return player()
