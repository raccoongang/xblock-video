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

YOUTUBE_VIDEO_URL_RE = re.compile(r'https?:\/\/(.+)?(wistia.com|wi.st)\/(medias|embed)\/.*')


class PlayerMissingError(Exception):
    pass


class BaseVideoPlayer(Plugin):
    __metaclass__ = abc.ABCMeta

    entry_point = 'video_xblock.v1'

    @abc.abstractproperty
    def url_regexes(self):
        return []

    @abc.abstractmethod
    def get_frag(self, context={}):
        return Fragment('<video />')

    def resource_string(self, path):
        """Handy helper for getting resources from our kit."""
        data = pkg_resources.resource_string(__name__, path)
        return data.decode("utf8")


class DummyPlayer(BaseVideoPlayer):
    @property
    def url_regexes(self):
        return [re.compile(r'')]

    def get_frag(self, **context):
        return Fragment(u'[Here be Video]')

    def media_id(self, href):
        return ''


class YoutubePlayer(BaseVideoPlayer):
    @property
    def url_regexes(self):
        # http://regexr.com/3a2p0
        return [re.compile(r'(?:youtube\.com\/\S*(?:(?:\/e(?:mbed))?\/|watch\?(?:\S*?&?v\=))|youtu\.be\/)([a-zA-Z0-9_-]{6,11})')]

    def media_id(self, href):
        return self.url_regexes[0].search(href).group(1)

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
    @property
    def url_regexes(self):
        return [re.compile(r'https:\/\/studio.brightcove.com\/products\/videocloud\/media\/videos\/(\d+)')]

    def media_id(self, href):
        return self.url_regexes[0].match(href).group(1)

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

    player_name = String(default='dummy-player',
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
        if data.href == '':# and not VIDEO_URL_RE.match(data.href):
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
        player = self.get_player()
        return player.get_frag(
            url=self.href, autoplay=False, account_id=self.account_id,
            video_id=player.media_id(self.href)
        )

    def clean_studio_edits(self, data):
        data['player_name'] = 'dummy-player'  # XXX: use field's default
        for player_name, player_class in BaseVideoPlayer.load_classes():
            if player_name == 'dummy-player':
                continue
            player = player_class()
            if any(regex.search(data['href']) for regex in player.url_regexes):
                data['player_name'] = player_name

    def get_player(self):
        player = BaseVideoPlayer.load_class(self.player_name)
        return player()
