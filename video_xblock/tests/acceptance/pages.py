"""
Page objects to use in tests.
"""

from .element import IdPageElement, ClassPageElement


class VideoJsPlayerElement(IdPageElement):
    """
    Root VideoJs player element.
    """

    locator = 'video_player_block_id'


class VideoJsPlayButton(ClassPageElement):
    """
    VideoJs play button located on the control bar.
    """

    locator = 'vjs-play-control'


class VideojsPlayerPage(object):
    """
    Page
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
