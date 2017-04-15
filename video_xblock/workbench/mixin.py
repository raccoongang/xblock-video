"""
Workbench mixin adds XBlock SDK workbench runtime support
"""

from video_xblock.utils import loader


class WorkbenchMixin(object):

    @staticmethod
    def workbench_scenarios():
        """A canned scenarios for display in the workbench."""

        return loader.load_scenarios_from_path('workbench/scenarios')
