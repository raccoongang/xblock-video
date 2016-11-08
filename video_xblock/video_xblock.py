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


class BaseVideoPlayer(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractproperty
    def url_regexes(self):
        return []

    @abc.abstractmethod
    def render_player(self, context={}):
        return Fragment('<video />')

    entry_point = 'video_xblock.v1'

    def resource_string(self, path):
        """Handy helper for getting resources from our kit."""
        data = pkg_resources.resource_string(__name__, path)
        return data.decode("utf8")

    @classmethod
    def _load_class_entry_point(cls, entry_point):
        """
        Load `entry_point`, and set the `entry_point.name` as the
        attribute `plugin_name` on the loaded object
        """
        class_ = entry_point.load()
        setattr(class_, 'plugin_name', entry_point.name)
        return class_

    @classmethod
    def load_players(cls, fail_silently=True):
        """ Utility method to load all players listed as entry points """
        all_classes = itertools.chain(
            pkg_resources.iter_entry_points(cls.entry_point),
            # (entry_point for identifier, entry_point in cls.extra_entry_points),
        )
        for class_ in all_classes:
            try:
                yield (class_.name, cls._load_class_entry_point(class_))
            except Exception:  # pylint: disable=broad-except
                if fail_silently:
                    log.warning('Unable to load %s %r', cls.__name__, class_.name, exc_info=True)
                else:
                    raise

    @classmethod
    def load_player(cls, video_url):
        """
        Utility method to load a player from entry points which matches
        the given video_url
        """
        for player_name, player_class in cls.load_players():
            player = player_class()
            if any(regex.search(video_url) for regex in player.url_regexes):
                return player

        return DummyPlayer()


class DummyPlayer(BaseVideoPlayer):
    @property
    def url_regexes(self):
        return [re.compile(r'.*')]

    def render_player(self, context={}):
        return Fragment()


class YoutubePlayer(BaseVideoPlayer):

    @property
    def url_regexes(self):
        # http://regexr.com/3a2p0
        return [re.compile(r'(?:youtube\.com\/\S*(?:(?:\/e(?:mbed))?\/|watch\?(?:\S*?&?v\=))|youtu\.be\/)([a-zA-Z0-9_-]{6,11})')]

    def render_player(self, context={}):
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


class VideoXBlock(StudioEditableXBlockMixin, XBlock):

    icon_class = "video"

    display_name = String(
        default='Video',
        display_name=_('Component Display Name'),
        help=_('The name students see. This name appears in the course ribbon and as a header for the video.'),
        scope=Scope.settings,
    )

    href = String(
        default='',
        display_name=_('Video URL'),
        help=_('URL of the video page. E.g. https://example.wistia.com/medias/12345abcde'),
        scope=Scope.content
    )

    editable_fields = ('display_name', 'href')

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
        The primary view of the WistiaVideoXBlock, shown to students
        when viewing courses.
        """
        player = self.get_player(self.href)
        return player.render_player({'url': self.href, 'autoplay': False})

    def get_player(self, href):
        player = BaseVideoPlayer.load_player(self.href)
        return player
