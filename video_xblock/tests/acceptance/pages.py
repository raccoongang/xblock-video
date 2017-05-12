from .element import BasePageElement, ClassPageElement


class VideoJsPlayerElement(BasePageElement):
    locator = 'video_player_block_id'


class VideoJsPlayButton(ClassPageElement):
    """docstring for VideoJsPlayButton"""
    locator = 'vjs-play-control'


class VideojsPlayerPage(object):
    player_element = VideoJsPlayerElement()
    play_button = VideoJsPlayButton()

    def __init__(self, driver):
        self.driver = driver

    def is_playing(self):
        return 'vjs-playing' in self.player_element.get_attribute('class')

