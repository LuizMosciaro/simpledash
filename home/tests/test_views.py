from http import HTTPStatus

from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse
from home.models import Asset
from home.forms import SignUpForm, NewAssetForm

class TestHomeView(TestCase):
    
    def setUp(self):
        self.client = Client()
        self.home_url = reverse('home')
        
    def test_home_get_returns_correct_html(self):
        response = self.client.get(self.home_url)
        
        self.assertEqual(response.status_code,HTTPStatus.OK)
        self.assertTemplateUsed(response,'home/index.html')

    def test_home_sidebar_items_presence(self):
        response = self.client.get(self.home_url).content.decode()
        self.assertIn('<title>SimpleDash</title>',response)
        self.assertIn('Dashboard',response)
        self.assertIn('Menu',response)
        self.assertIn('Portfolio',response)
        self.assertIn('Strategies',response)
        self.assertIn('Wallet',response)
        self.assertIn('Rewards',response)
        self.assertIn('Market Analysis',response)
        self.assertIn('Logout',response)

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
        data = {'username':'testuser','password':'testpassword'}
        response = self.client.post(self.login_url,data)
        self.assertRedirects(response,reverse('home'))
    
    def test_invalid_form_submission(self):
        data = {'username':'testuser','password':'wrongpassword'}
        response = self.client.post(self.login_url,data)
        self.assertContains(response,'Invalid credentials')

class TestSignUpView(TestCase):

    def setUp(self):
        self.client = Client()
        self.signup_url = reverse('signup')
    
    def test_signup_get_returns_correct_html(self):
        response = self.client.get(self.signup_url)

        self.assertEqual(response.status_code,HTTPStatus.OK)
        self.assertTemplateUsed(response,'home/signup.html')
        self.assertIn('Sign Up',response.content.decode())
    
    def test_signup_form_valid(self):
        form_data = {
            'username':'testuser',
            'first_name':'FirstName',
            'last_name':'LastName',
            'email':'testuser@example.com',
            'password1': '(H&*lhjikW#$%^CEI&*)',
            'password2': '(H&*lhjikW#$%^CEI&*)',
        }
        form = SignUpForm(form_data)
        
        self.assertTrue(form.is_valid())

    def test_signup_username_required(self):
        form_data = {
            'username':'',
            'first_name':'FirstName',
            'last_name':'LastName',
            'email':'testuser@example.com',
            'password1': '(H&*lhjikW#$%^CEI&*)',
            'password2': '(H&*lhjikW#$%^CEI&*)',
        }
        form = SignUpForm(form_data)

        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['username'],['Este campo é obrigatório.'])
    
    def test_signup_email_invalid(self):
        form_data = {
            'username':'testuser',
            'first_name':'FirstName',
            'last_name':'LastName',
            'email':'testemail',
            'password1': '(H&*lhjikW#$%^CEI&*)',
            'password2': '(H&*lhjikW#$%^CEI&*)',
        }
        form = SignUpForm(form_data)

        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['email'],['Informe um endereço de email válido.'])
    
    def test_signup_password_not_match(self):
        form_data = {
            'username':'testuser',
            'first_name':'FirstName',
            'last_name':'LastName',
            'email':'testuser@example.com',
            'password1': '(H&*lhjikW#$%^CEI&)',
            'password2': '(H&*lhjikW#$%^CEI&*)',
        }
        form = SignUpForm(form_data)

        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['password2'],['Os dois campos de senha não correspondem.'])

    def test_signup_create_new_user_and_redirects(self):
        form_data = {
            'username':'testuser',
            'first_name':'FirstName',
            'last_name':'LastName',
            'email':'testuser@example.com',
            'password1': '(H&*lhjikW#$%^CEI&*)',
            'password2': '(H&*lhjikW#$%^CEI&*)',
        }
        form = SignUpForm(form_data)

        self.assertTrue(form.is_valid())
        user = form.save()

        existing_user = User.objects.get(username='testuser')
        self.assertEqual(existing_user.username,user.username)

        response = self.client.post(reverse('signup'), data=form_data)
        self.assertEqual(response.status_code,HTTPStatus.OK)

class InvestmentsViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.investments_url = reverse('investments')
    
    def test_get_http_and_return_correct_html(self):
        response = self.client.get(self.investments_url)

        self.assertEqual(response.status_code,HTTPStatus.OK)
        self.assertTemplateUsed(response,'home/investments.html')
        self.assertIn('Investments',response.content.decode())

    def test_asset_form_valid(self):
        form_data = {
            'symbol':'ABC3',
            'amount':'100',
            'operation':'Buy',
        }
        form = NewAssetForm(form_data)
        self.assertTrue(form.is_valid())

    def test_asset_form_fields_required(self):
        form_data = {
            'symbol':'',
            'amount':'',
            'operation':'',
        }
        form = NewAssetForm(form_data)

        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['symbol'],['Este campo é obrigatório.'])
        self.assertEqual(form.errors['amount'],['Este campo é obrigatório.'])
        self.assertEqual(form.errors['operation'],['Este campo é obrigatório.'])
    
    def test_asset_form_add_new_investment(self):
        form_data = {
            'symbol':'ABC3',
            'amount':'100',
            'operation':'Buy',
        }
        form = NewAssetForm(form_data)
        self.assertTrue(form.is_valid())
        asset = form.save()
        
        existing_asset = Asset.objects.get(symbol='ABC3')
        self.assertEqual(asset.symbol,existing_asset.symbol)