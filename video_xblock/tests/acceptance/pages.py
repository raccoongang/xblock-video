"""
TODO.
"""

from .element import IdPageElement, ClassPageElement


class VideoJsPlayerElement(IdPageElement):
    """
    TODO.
    """

    locator = 'video_player_block_id'


class VideoJsPlayButton(ClassPageElement):
    """
    TODO.
    """

    locator = 'vjs-play-control'


class VideojsPlayerPage(object):
    """
    TODO.
    """

    player_element = VideoJsPlayerElement()
    play_button = VideoJsPlayButton()

    def __init__(self, driver):
        """
        TODO.
        """
        self.driver = driver

    def is_playing(self):
        """
        TODO.
        """
        return 'vjs-playing' in self.player_element.get_attribute('class')  # pylint: disable=no-member
