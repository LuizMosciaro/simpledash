from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options
from webdriver_manager.firefox import GeckoDriverManager
import unittest

class HomePageTest(unittest.TestCase):

    def setUp(self):
        options = Options()
        options.add_argument('-headless')
        manager = GeckoDriverManager().install()
        driver = webdriver.Firefox(options=options, service=FirefoxService(manager))
        self.driver = driver

    def tearDown(self):
        self.driver.quit()

    def test_can_check_home_items(self):
        #Users visit our homepage
        self.driver.get('http://127.0.0.1:8000/')

        #The users see the browser title
        self.assertIn('SimpleDash',self.driver.title)

        #They see the Greetings msg and the temperature text
        div_content1 = self.driver.find_element(By.ID,'content1')
        self.assertIn('Greetings',div_content1.text)
        self.assertTrue(div_content1)

        #Looking around other elements from the page
        div_content4 = self.driver.find_element(By.ID,'content4')
        self.assertTrue(div_content4)

        div_content5 = self.driver.find_element(By.ID,'content5')
        self.assertTrue(div_content5)

        div_content6 = self.driver.find_element(By.ID,'content6')
        self.assertTrue(div_content6)

        div_content7 = self.driver.find_element(By.ID,'content7')
        self.assertTrue(div_content7)

        div_content8 = self.driver.find_element(By.ID,'content8')
        self.assertTrue(div_content8)

        div_content9 = self.driver.find_element(By.ID,'content9')
        self.assertTrue(div_content9)

        sidebar = self.driver.find_element(By.ID,'sidebar')
        self.assertTrue(sidebar)

        div_main = self.driver.find_element(By.XPATH,'//main')
        self.assertTrue(div_main)


if __name__ == '__main__':  
    unittest.main()