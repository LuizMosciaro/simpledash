from django.test import TestCase
from django.urls import reverse, resolve
from home.views import home

class TestUrlHome(TestCase):
    
    def test_home_url_is_resolved(self):
        url = resolve('/')
        url2 = resolve('/home')
        
        self.assertEquals(url.func,home)
        self.assertEquals(url2.func,home)
