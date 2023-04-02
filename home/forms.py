from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Asset

class LoginForm(forms.Form):
    username = forms.CharField(label='Username',max_length=100)
    password = forms.CharField(widget=forms.PasswordInput())

class SignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=False)
    last_name = forms.CharField(max_length=30, required=False)
    email = forms.EmailField(max_length=200)

    class Meta:
        model = User
        fields = ('username','first_name','last_name','email','password1','password2',)

class NewAssetForm(forms.ModelForm):
    class Meta:
        model = Asset
        fields = ('symbol','amount','operation',)
        widgets = {
               'operation': forms.RadioSelect(),
           } 
