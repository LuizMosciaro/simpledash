from http import HTTPStatus

from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse


class TestHomeView(TestCase):
    
    def setUp(self):
        self.client = Client()
        self.home_url = reverse('home')
        
    def test_home_get_returns_correct_html(self):
        response = self.client.get(self.home_url)
        
        self.assertEqual(response.status_code,HTTPStatus.OK)
        self.assertTemplateUsed(response,'home/index.html')

    def test_home_sidebar_items_presence(self):
        response = self.client.get(self.home_url)

        self.assertIn('<title>SimpleDash</title>',response.content.decode())
        self.assertIn('Dashboard',response.content.decode())
        self.assertIn('Menu',response.content.decode())
        self.assertIn('Portfolio',response.content.decode())
        self.assertIn('Strategies',response.content.decode())
        self.assertIn('Wallet',response.content.decode())
        self.assertIn('Rewards',response.content.decode())
        self.assertIn('Market Analysis',response.content.decode())
        self.assertIn('Logout',response.content.decode())

class TestLoginView(TestCase):

    def setUp(self):
        self.client = Client()
        self.login_url = reverse('login_view')
        self.user = User.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='testpassword'
        )
    
    def test_login_get_returns_correct_html(self):
        response = self.client.get(self.login_url)
        
        self.assertEqual(response.status_code,HTTPStatus.OK)
        self.assertTemplateUsed(response,'home/login.html')
        self.assertIn('<title>Login</title>',response.content.decode())

    def test_valid_form_submission(self):
        url = reverse('login_view')
        data = {'username':'testuser','password':'testpassword'}
        response = self.client.post(url,data)
        self.assertRedirects(response,reverse('home'))
    
    def test_invalid_form_submission(self):
        url = reverse('login_view')
        data = {'username':'testuser','password':'wrongpassword'}
        response = self.client.post(url,data)
        self.assertContains(response,'Invalid credentials')