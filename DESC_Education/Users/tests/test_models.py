from django.test import TestCase
from Users.models import CustomUser, VerificationCode
from django.utils import timezone


class CustomUserTest(TestCase):
    def setUp(self):
        CustomUser.objects.create_user(
            email="testemail@example.com", first_name="Test_First_Name",
            last_name="Test_Last_Name",
            )
        CustomUser.objects.create_user(
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



class VerificationCodeTest(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(email="testemail@example.com", first_name="Test_First_Name",
            last_name="Test_Last_Name", password="testpassword")

        VerificationCode.objects.create(
            user=self.user, code="1234", type=VerificationCode.REGISTRATION_TYPE,
        )


    def test_verification_code(self):
        code: VerificationCode = VerificationCode.objects.get(user=self.user)

        self.assertEqual(code.is_valid(), True)
        self.assertEqual(code.REGISTRATION_TYPE, "RG")

    def test_expired_verification_code(self):
        code: VerificationCode = VerificationCode.objects.get(user=self.user)

        code.created_at = timezone.now() - timezone.timedelta(minutes=35)
        code.save()

        self.assertEqual(code.is_valid(), False)


