from http import HTTPStatus

from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse

from home.forms import NewAssetForm, SignUpForm, UpdateProfileForm
from home.models import Asset


class TestHomeView(TestCase):
    
    def setUp(self):
        self.client = Client()
        self.home_url = reverse('home')
        
    def test_home_get_returns_correct_html(self):
        response = self.client.get(self.home_url)
        
        self.assertEqual(response.status_code,HTTPStatus.OK)
        self.assertTemplateUsed(response,'home/index.html')

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
        self.assertEqual(response.status_code,HTTPStatus.OK)
    
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

        #Creating an user as the view its protected
        self.user = User.objects.create_user(
            username='testuser',
            email='testuser@test.com',
            password='testpass'
        )
        
        #Login the user
        self.client.login(
                username='testuser',
                password='testpass'
            )

    def test_get_http_and_return_correct_html(self):
        response = self.client.get(self.investments_url)

        self.assertEqual(response.status_code,HTTPStatus.OK)
        self.assertTemplateUsed(response,'home/investments.html')
        self.assertIn('Investments',response.content.decode())

    def test_asset_form_valid(self):
        form_data = {
            'symbol':'ABC3',
            'amount':'100',
            'price':'25.76',
            'operation':'Buy',
            'operation_date':'05/03/2023',
        }
        form = NewAssetForm(form_data)
        self.assertTrue(form.is_valid())

    def test_asset_form_fields_required(self):
        form_data = {
            'symbol':'',
            'amount':'',
            'operation':'',
            'price':'',
            'operation_date':'',
        }
        form = NewAssetForm(form_data)

        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['symbol'],['Este campo é obrigatório.'])
        self.assertEqual(form.errors['amount'],['Este campo é obrigatório.'])
        self.assertEqual(form.errors['price'],['Este campo é obrigatório.'])
        self.assertEqual(form.errors['operation'],['Este campo é obrigatório.'])
        self.assertEqual(form.errors['operation_date'],['Este campo é obrigatório.'])
    
    def test_asset_form_add_new_investment(self):
        form_data = {
            'symbol':'ABC3',
            'amount':'100',
            'price':'25.76',
            'operation':'Buy',
            'operation_date':'05/03/2023',
        }
        form = NewAssetForm(form_data)
        self.assertTrue(form.is_valid())
        asset = form.save()
        
        existing_asset = Asset.objects.get(symbol='ABC3')
        self.assertEqual(asset.symbol,existing_asset.symbol)
    
    def test_asset_form_delete_investment(self):
        form_data = {
            'symbol':'ABC3',
            'amount':'100',
            'price':'25.76',
            'operation':'Buy',
            'operation_date':'05/03/2023',
        }
        form = NewAssetForm(form_data)
        self.assertTrue(form.is_valid())
        form.save()
        
        existing_asset = Asset.objects.filter(symbol='ABC3').first()
        self.assertIsNotNone(existing_asset)
        existing_asset.delete()

        self.assertIsNone(Asset.objects.filter(symbol='ABC3').first())

class ProfileViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.profile_url = reverse('profile')

        #Creating an user as the view its protected
        self.user = User.objects.create_user(
            username='testuser',
            first_name = 'Firstname',
            last_name = 'Lastname',
            email='testuser@test.com',
            password='testpass'
        )
        
        #Login the user
        self.client.login(
                username='testuser',
                password='testpass'
            )
        
    def test_profile_get_returns_correct_html(self):
        response = self.client.get(self.profile_url)

        self.assertEqual(response.status_code,HTTPStatus.OK)
        self.assertTemplateUsed(response,'home/profile.html')
        self.assertIn('Profile',response.content.decode())

    def test_profile_form_valid(self):
        form_data = {
            'first_name':'Secondname',
            'last_name':'SecondLastname',
            'email':'testuser@test.com'
        }
        form = UpdateProfileForm(form_data)

        self.assertTrue(form.is_valid())

    def test_profile_username_not_required(self):
        form_data = {
            'username':'',
            'first_name':'FirstName',
            'last_name':'LastName',
        }
        form = UpdateProfileForm(form_data)

        self.assertTrue(form.is_valid())
        
    # def test_signup_create_new_user_and_redirects(self):
    #     form_data = {
    #         'username':'testuser',
    #         'first_name':'FirstName',
    #         'last_name':'LastName',
    #         'email':'testuser@example.com',
    #         'password1': '(H&*lhjikW#$%^CEI&*)',
    #         'password2': '(H&*lhjikW#$%^CEI&*)',
    #     }
    #     form = SignUpForm(form_data)

    #     self.assertTrue(form.is_valid())
    #     user = form.save()

    #     existing_user = User.objects.get(username='testuser')
    #     self.assertEqual(existing_user.username,user.username)

    #     response = self.client.post(reverse('signup'), data=form_data)
    #     self.assertEqual(response.status_code,HTTPStatus.OK)