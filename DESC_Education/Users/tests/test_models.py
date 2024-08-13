from django.test import TestCase
from Users.models import CustomUser



class CustomUserTest(TestCase):
    def setUp(self):
        CustomUser.objects.create(
            email="testemail@example.com", first_name="Test_First_Name",
            last_name="Test_Last_Name",
            )
        CustomUser.objects.create(
            email="testemail2@example.com", first_name="Test_First_Name2",
            last_name="Test_Last_Name2",
        )

    def test_token_payload(self):
        FirstUser: CustomUser = CustomUser.objects.get(email='testemail@example.com')
        SecondUser: CustomUser = CustomUser.objects.get(email='testemail2@example.com')
        self.assertEqual(
            FirstUser.token_payload, {
                'email': "testemail@example.com",
                'first_name': "Test_First_Name",
                'last_name': "Test_Last_Name"})
        self.assertEqual(
            SecondUser.token_payload, {
                'email': "testemail2@example.com",
                'first_name': "Test_First_Name2",
                'last_name': "Test_Last_Name2"
            })




