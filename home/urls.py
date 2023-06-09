from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('home', views.home, name='home'),
    path('login', views.login_view, name='login_view'),
    path('logout', views.logout_view, name='logout_view'),
    path('signup', views.signup, name='signup'),
    path('investments', views.investments, name='investments'),
    path('investments/<int:item_id>', views.consult_investments, name='consult_investments'),
    path('delete_asset/<int:item_id>', views.delete_asset, name='delete_asset'),
    path('profile', views.profile, name='profile'),
] + static(settings.STATIC_URL,document_root=settings.STATIC_ROOT)
