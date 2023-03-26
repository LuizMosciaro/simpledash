from django.test import TestCase,Client
from django.urls import reverse

class TestViews(TestCase):
    
    def setUp(self):
        self.client = Client()
        self.home_url = reverse('home')
        

    def test_home_get(self):
        response = self.client.get(self.home_url)
        self.assertEquals(response.status_code,200)
        self.assertTemplateUsed(response,'home/index.html')
