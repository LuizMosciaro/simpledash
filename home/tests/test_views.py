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
        self.assertTrue(response.content.decode().endswith('</html>'))
        self.assertTemplateUsed(response,'home/index.html')
    