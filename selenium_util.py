### SELENIUM IMPORTS START ###
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.expected_conditions import visibility_of_element_located, visibility_of_all_elements_located, presence_of_all_elements_located
from selenium.webdriver.support.wait import WebDriverWait
### SELENIUM IMPORTS END ###

import time, os


class SeleniumUtil:

    def __init__(self):
        self.driver = self.get_new_driver_obj()
    
    def get_new_driver_obj(self):
        option = webdriver.ChromeOptions()

        option.add_argument('--headless')
        option.add_argument('--no-sandbox')
        option.add_argument('--disable-dev-sh-usage')

        options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")

        # Custom header for language
        option.add_argument('accept-language=en-US')

        executable_path = os.environ.get("CHROMEDRIVER_PATH")

        service = Service(executable_path=executable_path)
        driver = webdriver.Chrome(service=service, options=option)

        return driver