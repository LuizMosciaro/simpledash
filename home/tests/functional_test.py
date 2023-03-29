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

        #[...continue]
        print('Finished')

if __name__ == '__main__':  
    unittest.main()