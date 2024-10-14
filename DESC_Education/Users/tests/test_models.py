from django.test import TestCase
from Users.models import CustomUser, VerificationCode
from django.utils import timezone


class CustomUserTest(TestCase):
    def setUp(self):
        CustomUser.objects.create_user(
            email="testemail@example.com",
            password="testpassword"
            )
        CustomUser.objects.create_user(
            email="testemail2@example.com",
            password="testpassword"
        )
        CustomUser.objects.create_superuser(
            email="testemail3@example.com",
            password="testpassword")

    def test_token_payload(self):
        FirstUser: CustomUser = CustomUser.objects.get(email='testemail@example.com')
        SecondUser: CustomUser = CustomUser.objects.get(email='testemail2@example.com')
        self.assertEqual(
            FirstUser.token_payload, {
                'id': FirstUser.id,
                'email': "testemail@example.com",
            })
        self.assertEqual(
            SecondUser.token_payload, {
                "id": SecondUser.id,
                'email': "testemail2@example.com",
            })

    def test_user(self):
        user: CustomUser = CustomUser.objects.get(email='testemail@example.com')

        self.assertEqual(str(user), user.email)

    def test_create_user_without_mail(self):
        with self.assertRaises(ValueError):
            CustomUser.objects.create_user(email=None, password="123")


    def test_delete(self):
        self.assertEqual(3, CustomUser.objects.all().count())

        user: CustomUser = CustomUser.objects.get(email="testemail@example.com")
        user.soft_delete()

        self.assertEqual(2, CustomUser.objects.all().count())
        self.assertEqual(3, CustomUser.all_objects.all().count())











class VerificationCodeTest(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(email="testemail@example.com", password="testpassword")

        VerificationCode.objects.create(
            user=self.user, code="1234", type=VerificationCode.REGISTRATION_TYPE,
        )


    def test_verification_code(self):
        code: VerificationCode = VerificationCode.objects.get(user=self.user)

        self.assertEqual(code.is_valid(), True)
        self.assertEqual(code.REGISTRATION_TYPE, "RG")

    def test_expired_verification_code(self):
        code: VerificationCode = VerificationCode.objects.get(user=self.user)

        code.created_at = timezone.now() - timezone.timedelta(minutes=VerificationCode.EXPIRED_SECONDS + 5)
        code.save()

        self.assertEqual(code.is_valid(), False)


