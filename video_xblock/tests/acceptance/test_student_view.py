from time import sleep

from ddt import data, ddt

from xblockutils.base_test import SeleniumXBlockTest
from xblockutils.studio_editable_test import StudioEditableBaseTest

from video_xblock.utils import loader

from .pages import VideojsPlayerPage


@ddt
class TestStudentView(SeleniumXBlockTest):
    """
    Test the Student View of MyCoolXBlock
    """

    def load_scenario(self, xml_file, params=None, load_immediately=True):
        """
        Given the name of an XML file in the xml_templates folder, load it into the workbench.
        """
        params = params or {}
        scenario = loader.load_unicode("workbench/scenarios/{}".format(xml_file))
        print(scenario)
        self.set_scenario_xml(scenario)
        if load_immediately:
            view = self.go_to_view("student_view")
            self.driver.switch_to.frame('xblock-video-player')
            return view

    @data('brightcove.xml', 'youtube.xml', 'vimeo.xml', 'wistia.xml')
    def test_video_player_can_play_video(self, scenario):
        """
        The xblock should display the text value of field2.
        """
        # Arrange
        wrapper = self.load_scenario(scenario)
        vjs_player = VideojsPlayerPage(self.driver)

        # Act
        self.assertIsNotNone(wrapper)
        self.assertFalse(vjs_player.is_playing())
        vjs_player.play_button.click()
        sleep(1)  # TODO: Change to promise

        # Assert
        self.assertTrue(vjs_player.is_playing())
