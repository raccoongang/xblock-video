"""
Custom, VideoXblock specific Exceptions.
"""
from __future__ import unicode_literals

from .utils import ugettext as _


class VideoXBlockException(Exception):
    """
    Base class for video xblock exceptions.
    Subclasses should provide `.default_detail` property.
    """
    default_detail = _('An exception occurred.')

    def __init__(self, detail=None):
        self.detail = detail if detail is not None else self.default_detail
        super(VideoXBlockException, self).__init__(detail)

    def __str__(self):
        return self.detail


class ApiClientError(VideoXBlockException):
    """
    Base API client exception.
    """
    default_detail = _('API error occurred.')
