from xblockutils.base_test import SeleniumXBlockTest
from xblockutils.studio_editable_test import StudioEditableBaseTest

from video_xblock.utils import loader


class TestStudentView(SeleniumXBlockTest):
    """
    Test the Student View of MyCoolXBlock
    """

    def load_scenario(self, xml_file, params=None, load_immediately=True):
        """
        Given the name of an XML file in the xml_templates folder, load it into the workbench.
        """
        params = params or {}
        scenario = loader.render_django_template("workbench/scenarios/{}".format(xml_file), params)
        self.set_scenario_xml(scenario)
        if load_immediately:
            return self.go_to_view("student_view")

    def test_hello_world(self):
        """
        The xblock should display the text value of field2.
        """
        wrapper = self.load_scenario('youtube.xml')
        self.driver.switch_to_frame('xblock-video-player')
        player_container = self.driver.find_element_by_id('video_player_block_id')
        self.assertIsNotNone(player_container)
