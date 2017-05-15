"""
Page elements to use with page objects.
"""

from selenium.webdriver.support.ui import WebDriverWait


class IdPageElement(object):
    """
    Page element wich finds itself by id attribute.
    """

    def __get__(self, obj, owner):
        """
        Get the element of the specified object.
        """
        driver = obj.driver
        WebDriverWait(driver, 100).until(
            lambda driver: driver.find_element_by_id(self.locator))  # pylint: disable=no-member
        element = driver.find_element_by_id(self.locator)  # pylint: disable=no-member
        return element


class ClassPageElement(object):
    """
    Page element wich finds itself by class attribute.
    """

    def __get__(self, obj, owner):
        """
        Get the element of the specified object.
        """
        driver = obj.driver
        WebDriverWait(driver, 100).until(
            lambda driver: driver.find_element_by_class_name(self.locator))  # pylint: disable=no-member
        element = driver.find_element_by_class_name(self.locator)  # pylint: disable=no-member
        return element


class InputPageElement(object):
    """
    Input page element.

    Locates element by its name, can get and set element's text value.
    """

    def __set__(self, obj, value):
        """
        Set the text to the value supplied.
        """
        driver = obj.driver
        WebDriverWait(driver, 100).until(
            lambda driver: driver.find_element_by_name(self.locator))  # pylint: disable=no-member
        driver.find_element_by_name(self.locator).send_keys(value)  # pylint: disable=no-member

    def __get__(self, obj, owner):
        """
        Get the text value of the specified object.
        """
        driver = obj.driver
        WebDriverWait(driver, 100).until(
            lambda driver: driver.find_element_by_name(self.locator))  # pylint: disable=no-member
        element = driver.find_element_by_name(self.locator)  # pylint: disable=no-member
        return element.get_attribute('value')
