"""
TODO.
"""

from selenium.webdriver.support.ui import WebDriverWait


class IdPageElement(object):
    """
    TODO.

    Base page class that is initialized on every page object class.
    """

    def __get__(self, obj, owner):
        """
        Get the text of the specified object.
        """
        driver = obj.driver
        WebDriverWait(driver, 100).until(
            lambda driver: driver.find_element_by_id(self.locator))  # pylint: disable=no-member
        element = driver.find_element_by_id(self.locator)  # pylint: disable=no-member
        return element


class ClassPageElement(object):
    """
    TODO.
    """

    def __get__(self, obj, owner):
        """
        Get the text of the specified object.
        """
        driver = obj.driver
        WebDriverWait(driver, 100).until(
            lambda driver: driver.find_element_by_class_name(self.locator))  # pylint: disable=no-member
        element = driver.find_element_by_class_name(self.locator)  # pylint: disable=no-member
        return element


class InputPageElement(object):
    """
    TODO.
    """

    def __set__(self, obj, value):
        """
        Set the text to the value supplied.
        """
        driver = obj.driver
        WebDriverWait(driver, 100).until(
            lambda driver: driver.find_element_by_id(self.locator))  # pylint: disable=no-member
        driver.find_element_by_id(self.locator).send_keys(value)  # pylint: disable=no-member

    def __get__(self, obj, owner):
        """
        Get the text of the specified object.
        """
        driver = obj.driver
        WebDriverWait(driver, 100).until(
            lambda driver: driver.find_element_by_id(self.locator))  # pylint: disable=no-member
        element = driver.find_element_by_id(self.locator)  # pylint: disable=no-member
        return element.get_attribute('value')
