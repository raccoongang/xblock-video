"""
Video XBlock provides a convenient way to place videos hosted on
Wistia platform.
All you need to provide is video url, this XBlock doest the rest for you.
"""

import pkg_resources
import re

import abc
import itertools
import logging

from webob import Response
from xblock.core import XBlock
from xblock.fields import Scope, Integer, String
from xblock.fragment import Fragment
from xblock.plugin import Plugin
from xblock.validation import ValidationMessage

from django.template import Template, Context

from xblockutils.studio_editable import StudioEditableXBlockMixin

import HTMLParser

html_parser = HTMLParser.HTMLParser()

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
        return [] or re.RegexObject or ''

    @abc.abstractmethod
    def get_frag(self, **context):
        return Fragment('<video />')

    @abc.abstractmethod
    def media_id(self, href):
        """
        Extracts Platform's media id from the video url.
        E.g. https://example.wistia.com/medias/12345abcde -> 12345abcde
        """

        return ''

    def get_player_html(self, **context):
        frag = self.get_frag(**context)
        return Response(
            frag.head_html()+frag.body_html()+frag.foot_html(),
            content_type='text/html')

    def resource_string(self, path):
        """Handy helper for getting resources from our kit."""
        data = pkg_resources.resource_string(__name__, path)
        return data.decode("utf8")

    def match(self, href):
        if isinstance(self.url_re, list):
            return any(regex.search(href) for regex in self.url_re)
        elif isinstance(self.url_re, re.RegexObject):
            return self.url_re.search(href)
        elif isinstance(self.url_re, basestring):
            return re.search(self.url_re, href, re.I)


class DummyPlayer(BaseVideoPlayer):
    @property
    def url_re(self):
        return [re.compile(r'')]

    def get_frag(self, **context):
        return Fragment(u'[Here be Video]')

    def media_id(self, href):
        return '<media_id>'


class YoutubePlayer(BaseVideoPlayer):
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
        frag.add_javascript(self.resource_string(
            'static/bower_components/videojs-youtube/dist/Youtube.min.js'
        ))

        return frag


class BrightcovePlayer(BaseVideoPlayer):
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


class VideoXBlock(StudioEditableXBlockMixin, XBlock):

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

    @property
    def media_id(self):
        """
        Extracts Wistia's media hashed id from the media url.
        E.g. https://example.wistia.com/medias/12345abcde -> 12345abcde
        """
        if self.href:
            return self.href.split('/')[-1]
        return ''

    def validate_field_data(self, validation, data):
        if data.href == '':
            return
        for player_name, player_class in BaseVideoPlayer.load_classes():
            player = player_class()
            if player.match(data.href):
                return

        validation.add(ValidationMessage(
            ValidationMessage.ERROR,
            _(u"Incorrect video url, please recheck")
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
        player = self.get_player()
        return player.get_player_html(
            url=self.href, autoplay=False, account_id=self.account_id,
            video_id=player.media_id(self.href))

    def clean_studio_edits(self, data):
        data['player_name'] = 'dummy-player'  # XXX: use field's default
        for player_name, player_class in BaseVideoPlayer.load_classes():
            if player_name == 'dummy-player':
                continue
            player = player_class()
            if player.match(data['href']):
                data['player_name'] = player_name

    def get_player(self):
        player = BaseVideoPlayer.load_class(self.player_name)
        return player()
