# -*- coding: utf-8 -*-
from bok_choy.page_object import PageObject


class StudioPage(PageObject):
    """
    GitHub's search page
    """

    url = 'http://www.github.com/search'

    def is_browser_on_page(self):
        return 'code search' in self.browser.title.lower()
