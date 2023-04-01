import time
from django.contrib.auth.models import User
from django.test import LiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.firefox import GeckoDriverManager

class HomePageTest(LiveServerTestCase):

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
        self.driver.get(self.live_server_url)

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

class LoginViewTest(LiveServerTestCase):

    def setUp(self):
        options = Options()
        options.add_argument('-headless')
        manager = GeckoDriverManager().install()
        driver = webdriver.Firefox(options=options, service=FirefoxService(manager))
        self.driver = driver
        self.user = User.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='testpassword'
        )

    def tearDown(self):
        self.driver.quit()

    def test_login_sucess(self):
        #Trying to reach the login page
        self.driver.get(self.live_server_url + '/login')
        
        #Assert login title is correct 
        self.assertEqual(self.driver.title,'Login')

        #Find the form inputs
        username = self.driver.find_element(By.NAME,'username')
        username.send_keys('testuser')

        password = self.driver.find_element(By.NAME,'password')
        password.send_keys('testpassword')

        #Submit the form
        password.send_keys(Keys.RETURN)

        #Waits content in the page
        element = EC.presence_of_element_located((By.ID,'content1'))
        WebDriverWait(self.driver,100).until(element)
        
        #Assert redirect to home page
        self.assertIn('/home',self.driver.current_url)

        # Assert error message is not present
        self.assertNotIn('Invalid credentials',self.driver.page_source)

class SignUpViewTest(LiveServerTestCase):

    def setUp(self):
        options = Options()
        options.add_argument('-headless')
        manager = GeckoDriverManager().install()
        driver = webdriver.Firefox(options=options, service=FirefoxService(manager))
        self.driver = driver

    def tearDown(self):
        self.driver.quit()

    def test_signup(self):
        #Checking the page
        self.driver.get(self.live_server_url + '/signup')

        #Confirm the title
        self.assertIn('Sign Up',self.driver.title)

        #Filling up the form
        username = self.driver.find_element(By.NAME,'username')
        username.send_keys('testuser')

        first_name = self.driver.find_element(By.NAME,'first_name')
        first_name.send_keys('FirstName')

        last_name = self.driver.find_element(By.NAME,'last_name')
        last_name.send_keys('LastName')

        email = self.driver.find_element(By.NAME,'email')
        email.send_keys('test@example.com')
        
        password1 = self.driver.find_element(By.NAME,'password1')
        password1.send_keys('superstrongpassword!9%')

        password2 = self.driver.find_element(By.NAME,'password2')
        password2.send_keys('superstrongpassword!9%')

        #Sending the user creation form
        password2.send_keys(Keys.RETURN)

        #Waits for element in the login page
        element = EC.presence_of_element_located((By.CLASS_NAME,'divForm'))
        WebDriverWait(self.driver,100).until(element)

        #Assert redirect
        self.assertIn('/login',self.driver.current_url)
