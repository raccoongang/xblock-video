"""
Utils for rendering videojs player.
"""
from django.conf import settings

from video_xblock.backends.brightcove import BrightcovePlayer
from video_xblock.backends.html5 import Html5Player
from video_xblock.backends.vimeo import VimeoPlayer
from video_xblock.backends.wistia import WistiaPlayer
from video_xblock.backends.youtube import YoutubePlayer


def get_player(player_name):
    """
    Helper method to load video player by entry-point label.

    Returns:
        Current player object (instance of a platform-specific player class).
    """
    players = {
        "brightcove": BrightcovePlayer,
        "html5": Html5Player,
        "vimeo": VimeoPlayer,
        "wistia": WistiaPlayer,
        "youtube": YoutubePlayer

    }
    if player_name in players:
        return players[player_name]


def player_data(player_name):
    """
    Get player data from settings.
    """
    data = settings.PLAYER_DATA
    if player_name in data:
        return data[player_name]


class obj(object):
    def __init__(self, d):
        for a, b in d.items():
            if isinstance(b, (list, tuple)):
                setattr(self, a, [obj(x) if isinstance(x, dict) else x for x in b])
            else:
                setattr(self, a, obj(b) if isinstance(b, dict) else b)
        setattr(self, 'metadata', {})
