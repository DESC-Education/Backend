from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from Users.models import CustomUser, CustomUserManager
from django.urls import reverse
import json



class LoginViewTest(APITestCase):

    @classmethod
    def setUpTestData(cls):
        # Set up data for the whole TestCase
        cls.user: CustomUser = CustomUser.objects.create_user(
            email="test@mail.com",
            first_name="first_name",
            last_name="last_name",
            password="test123",
            email_auth=True)


    def test_invalid_login(self):
        res = self.client.post(reverse('login'),
                               data=json.dumps({"email": "test@mail.com", "password": "wrong_password"}),
                               content_type="application/json")

        self.assertEqual(res.status_code, 401)
        self.assertEqual(res.data.get("message"), "Invalid email or password")

    def test_invalid_auth_mail(self):
        self.user.email_auth = False
        self.user.save()

        res = self.client.post(reverse('login'),
                               data=json.dumps({"email": "test@mail.com", "password": "test123"}),
                               content_type="application/json")

        self.assertEqual(res.status_code, 406)
        self.assertEqual(res.data.get("message"), "Need to verify email")

    def test_login(self):
        CustomUser.objects.get(email="test@mail.com")

        res = self.client.post(reverse('login'),
                               data=json.dumps({"email": "test@mail.com", "password": "test123"}),
                               content_type="application/json")

        self.assertEqual(res.status_code, 200)
        self.assertEqual(type(res.data.get("access_token")), str)
        self.assertEqual(type(res.data.get("refresh_token")), str)


class RegisterViewTest(APITestCase):


    def test_exist_registration(self):

        CustomUser.objects.create_user(email="test@mail.com", password="test123")


        res = self.client.post(reverse('register'),
                               data=json.dumps({"email": "test@mail.com", "password": "test123"}),
                               content_type="application/json")

        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.data, {'message': 'Email already registered'})



    def test_registration(self):
        res = self.client.post(reverse('register'),
                               data=json.dumps({"email": "test@mail.com", "password": "test123"}),
                               content_type="application/json")

        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data, {"message": "Authorization code sent to email"})





