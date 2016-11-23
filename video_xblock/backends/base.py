import abc
import pkg_resources
import re

from HTMLParser import HTMLParser
from webob import Response
from xblock.fragment import Fragment
from xblock.plugin import Plugin


html_parser = HTMLParser()


class BaseVideoPlayer(Plugin):
    """
    Inherit your video player class from this class
    """
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

        Rendering sequence is set to JS must be in the head tag and executed
        before initializing video components.
        """
        frag = self.get_frag(**context)
        return Response(
            u'<html><head>{}{}</head><body>{}</body></html>'.format(
                frag.head_html(), frag.foot_html(), frag.body_html()
            ),
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
