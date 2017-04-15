import os
from os import listdir
from os.path import basename

from xblockutils.resources import ResourceLoader

loader = ResourceLoader(__name__)


class WorkbenchMixin(object):

    @staticmethod
    # @XBlock.register_temp_plugin(youtube.YoutubePlayer, 'youtube')
    def workbench_scenarios():
        """A canned scenario for display in the workbench."""

        return loader.load_scenarios_from_path('scenarios')
