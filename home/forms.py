from django import forms
from django.contrib.auth.forms import UserCreationForm,UserChangeForm
from django.contrib.auth.models import User
from django.forms.widgets import DateInput

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

class UpdateProfileForm(UserChangeForm):

    class Meta:
        model = User
        fields = ('first_name','last_name','email',)
        widgets = {
            'first_name': forms.TextInput(attrs={'placeholder':'Optional'}),
            'last_name': forms.TextInput(attrs={'placeholder':'Optional'}),
            'email': forms.TextInput(attrs={'placeholder':'Optional'}),
        }

class NewAssetForm(forms.ModelForm):
    class Meta:
        model = Asset
        fields = ('symbol','amount','price','operation_date','operation',)
        widgets = {
               'operation': forms.RadioSelect(),
               'symbol': forms.TextInput(attrs={'placeholder':'Ex: PETR3'}),
               'amount': forms.TextInput(attrs={'placeholder':'Shares or Fractions'}),
               'price': forms.TextInput(attrs={'placeholder':''}),
               'operation_date': DateInput(attrs={'type': 'date'}),
           } 
