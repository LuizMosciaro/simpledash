from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('home', views.home, name='home'),
    path('login', views.login_view, name='login_view'),
    path('signup', views.signup, name='signup'),
] + static(settings.STATIC_URL,document_root=settings.STATIC_ROOT)
