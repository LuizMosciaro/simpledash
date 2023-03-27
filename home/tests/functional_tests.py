from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options
from webdriver_manager.firefox import GeckoDriverManager
import unittest


class HomePageTest(unittest.TestCase):

    def setUp(self):
        options = Options()
        #options.add_argument('-headless')
        manager = GeckoDriverManager().install()
        driver = webdriver.Firefox(options=options, service=FirefoxService(manager))

        self.driver = driver

    def tearDown(self):
        self.driver.quit()

    def test_can_check_home_items(self):
        #Users visit our homepage
        self.driver.get('http://192.168.1.105:5000')

        #They see the browser title
        self.assertIn('SimpleDash',self.driver.title)

        #[...continue]

if __name__ == '__main__':  
    unittest.main()