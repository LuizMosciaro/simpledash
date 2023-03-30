from django.test import TestCase,Client
from django.urls import reverse

class TestHomeView(TestCase):
    
    def setUp(self):
        self.client = Client()
        self.home_url = reverse('home')
        

    def test_home_get_returns_correct_html(self):
        response = self.client.get(self.home_url)
        self.assertEqual(response.status_code,200)
        self.assertIn('<title>SimpleDash</title>',response.content.decode())
        self.assertTemplateUsed(response,'home/index.html')

# class TestLoginView(TestCase):

#     def setUp(self):
#         self.client = Client()
#         self.home_url = reverse('login')
    
#     def test_login_get_returns_correct_html(self):
#         response = self.client.get(self.login)
#         self.assertEqual(response.status_code,200)