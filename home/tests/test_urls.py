from django.test import TestCase
from django.urls import reverse, resolve
from home.views import home

class TestUrls(TestCase):
    
    def test_list_url_is_resolved(self):
        url = reverse('home')
        self.assertEquals(resolve(url).func,home)