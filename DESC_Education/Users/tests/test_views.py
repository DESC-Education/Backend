from rest_framework.test import APITestCase
from Chats.models import Chat, ChatMembers, Message
from Users.models import (
    CustomUser,
    CustomUserManager,
    VerificationCode
)
from django.urls import reverse
import json
from django.utils import timezone


class LoginViewTest(APITestCase):

    @classmethod
    def setUpTestData(cls):
        # Set up data for the whole TestCase
        cls.user: CustomUser = CustomUser.objects.create_user(
            email="test@mail.com",
            password="test123",
            is_verified=True)

    def test_invalid_login_401(self):
        res = self.client.post(reverse('login'),
                               data=json.dumps({"email": "test@mail.com", "password": "wrong_password"}),
                               content_type="application/json")

        self.assertEqual(res.status_code, 401)
        self.assertEqual(res.data.get("message"), "Неверный адрес электронной почты или пароль")

    def test_invalid_login_401_2(self):
        res = self.client.post(reverse('login'),
                               data=json.dumps({"email": "wrong@mail.com", "password": "test123"}),
                               content_type="application/json")

        self.assertEqual(res.status_code, 401)
        self.assertEqual(res.data.get("message"), "Неверный адрес электронной почты или пароль")

    def test_invalid_auth_mail_406(self):
        self.user.is_verified = False
        self.user.save()

        res = self.client.post(reverse('login'),
                               data=json.dumps({"email": "test@mail.com", "password": "test123"}),
                               content_type="application/json")

        self.assertEqual(res.status_code, 406)
        self.assertEqual(res.data.get("message"), "Вам нужно подтвердить адрес электронной почты")

    def test_login_200(self):
        CustomUser.objects.get(email="test@mail.com")

        res = self.client.post(reverse('login'),
                               data=json.dumps({"email": "test@mail.com", "password": "test123"}),
                               content_type="application/json")

        tokens = dict(res.data).get('tokens')

        self.assertEqual(res.status_code, 200)
        self.assertEqual(dict(res.data).get("user"),
                         {
                             "id": str(self.user.id),
                             "email": self.user.email,
                             "role": self.user.role,
                             "isActive": self.user.is_active,
                             "isStaff": self.user.is_staff,
                             "isSuperuser": self.user.is_superuser,
                             "isVerified": self.user.is_verified,
                             'createdAt': self.user.created_at.isoformat(),
                             "unreadChatsCount": 0,
                             'notifications': []
                         }
                         )
        self.assertEqual(type(tokens.get("accessToken")), str)
        self.assertEqual(type(tokens.get("refreshToken")), str)


class RegistrationViewTest(APITestCase):

    def test_exist_registration_406(self):
        CustomUser.objects.create_user(email="test@mail.com", password="test123")

        res = self.client.post(reverse('registration'),
                               data=json.dumps({"email": "test@mail.com", "password": "test123"}),
                               content_type="application/json")

        self.assertEqual(res.status_code, 406)
        self.assertEqual(res.data, {'message': 'Адрес электронной почты уже зарегистрирован'})

    def test_registration_default_200(self):
        res = self.client.post(reverse('registration'),
                               data=json.dumps({"email": "test@mail.com", "password": "test123"}),
                               content_type="application/json")

        user: CustomUser = CustomUser.objects.get(email="test@mail.com")

        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data, {"message": 'Код подтверждения отправлен на электронную почту'})
        self.assertEqual(user.role, user.STUDENT_ROLE)
        self.assertEqual(user.is_verified, False)

    def test_registration_company_200(self):
        res = self.client.post(reverse('registration'),
                               data=json.dumps({
                                   "email": "test@mail.com",
                                   "password": "test123",
                                   "role": CustomUser.COMPANY_ROLE
                               }),
                               content_type="application/json")

        user: CustomUser = CustomUser.objects.get(email="test@mail.com")

        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data, {"message": 'Код подтверждения отправлен на электронную почту'})
        self.assertEqual(user.role, user.COMPANY_ROLE)
        self.assertEqual(user.is_verified, False)




class CustomTokenRefreshViewTest(APITestCase):

    def setUp(self):
        # Set up data for the whole TestCase
        self.user: CustomUser = CustomUser.objects.create_user(
            email="test@mail.com",
            password="test123",
            is_verified=True)

        res = self.client.post(reverse('login'),
                               data=json.dumps({"email": "test@mail.com", "password": "test123"}),
                               content_type="application/json")

        self.refresh_token = dict(res.data).get("tokens").get("refreshToken")

    def test_token_refresh_200(self):
        res = self.client.post(reverse('token_refresh'),
                               data=json.dumps({"refresh": self.refresh_token}),
                               content_type="application/json")

        self.assertEqual(type(res.data.get("access")), str)
        self.assertEqual(res.status_code, 200)

    def test_invalid_token_refresh_401(self):
        res = self.client.post(reverse('token_refresh'),
                               data=json.dumps({"refresh": self.refresh_token[::-1]}),
                               content_type="application/json")

        self.assertEqual(res.data.get("detail"), "Токен недействителен или просрочен")
        self.assertEqual(res.status_code, 401)


class VerifyRegistrationViewTest(APITestCase):

    def setUp(self):
        # Set up data for the whole TestCase
        self.user: CustomUser = CustomUser.objects.create_user(
            email="test@mail.com",
            password="test123",
        )
        CustomUser.objects.create_user(
            email="test2@mail.com",
            password="test123",
        )

        VerificationCode.objects.create(
            user=self.user, code=1234, type=VerificationCode.REGISTRATION_TYPE,
        )

    def test_verify_registration_200(self):
        res = self.client.post(reverse('verify_registration'),
                               data=json.dumps({"email": "test@mail.com",
                                                "code": 1234}),
                               content_type="application/json")

        user: CustomUser = CustomUser.objects.get(email="test@mail.com")
        code: VerificationCode = VerificationCode.objects.get(user=user)

        self.assertEqual(dict(res.data).get('user'),
                         {
                             "id": str(user.id),
                             "email": user.email,
                             "role": user.role,
                             "isActive": user.is_active,
                             "isStaff": user.is_staff,
                             "isSuperuser": user.is_superuser,
                             "isVerified": user.is_verified,
                             'createdAt': user.created_at.isoformat(),
                             'unreadChatsCount': 0,
                             'notifications': []
                         })
        self.assertEqual(res.status_code, 200)
        self.assertTrue(user.is_verified)
        self.assertTrue(code.is_used)

    def test_invalid_user_404(self):
        res = self.client.post(reverse('verify_registration'),
                               data=json.dumps({"email": "wrong_email@mail.com",
                                                "code": 1234}),
                               content_type="application/json")
        self.assertEqual(res.status_code, 404)
        self.assertEqual(res.data, {"message": "Пользователь не найден"})

    def test_invalid_code_DoesNotExist_406(self):
        res = self.client.post(reverse('verify_registration'),
                               data=json.dumps({"email": "test2@mail.com",
                                                "code": 1234}),
                               content_type="application/json")
        self.assertEqual(res.status_code, 406)
        self.assertEqual(res.data, {"message": 'Проверочный код не существует или не соответствует'})

    def test_incorrect_code_406(self):
        res = self.client.post(reverse('verify_registration'),
                               data=json.dumps({"email": "test@mail.com",
                                                "code": 1224}),
                               content_type="application/json")

        self.assertEqual(res.status_code, 406)
        self.assertEqual(res.data, {"message": 'Проверочный код не существует или не соответствует'})

    def test_expired_code_403(self):
        code: VerificationCode = VerificationCode.objects.get(user=self.user)
        code.created_at = timezone.now() - timezone.timedelta(days=2)
        code.save()
        res = self.client.post(reverse('verify_registration'),
                               data=json.dumps({"email": "test@mail.com",
                                                "code": 1234}),
                               content_type="application/json")

        self.assertEqual(res.status_code, 403)
        self.assertEqual(res.data, {"message": 'Срок действия проверочного кода истек, запросите новый'})


class AuthViewTest(APITestCase):
    def setUp(self):
        self.user: CustomUser = CustomUser.objects.create_user(
            email="test@mail.com",
            password="test123",
            is_verified=True,
        )
        self.company = CustomUser.objects.create_user(
            email="test_company@mail.com",
            password="test123",
            role=CustomUser.COMPANY_ROLE,
            is_verified=True,
        )
        self.chat = Chat.objects.create()
        ChatMembers.objects.create(user=self.user, chat=self.chat)
        ChatMembers.objects.create(user=self.company, chat=self.chat)
        Message.objects.create(chat=self.chat, message="123", user=self.user)
        Message.objects.create(chat=self.chat, message="123", user=self.company)
        Message.objects.create(chat=self.chat, message="123", user=self.company)

        self.chat = Chat.objects.create()
        ChatMembers.objects.create(user=self.user, chat=self.chat)
        ChatMembers.objects.create(user=self.company, chat=self.chat)
        Message.objects.create(chat=self.chat, message="123", user=self.company)

    def test_auth_200(self):
        tokens = self.user.get_token()
        res = self.client.get(reverse('auth'), headers={"Authorization": f"Bearer {tokens.get('accessToken')}"},
                              content_type="application/json")


        self.assertEqual(dict(res.data), {
                    "id": str(self.user.id),
                    "email": self.user.email,
                    "role": self.user.role,
                    "isActive": self.user.is_active,
                    "isStaff": self.user.is_staff,
                    "isSuperuser": self.user.is_superuser,
                    "isVerified": self.user.is_verified,
                    'createdAt': self.user.created_at.isoformat(),
                    'notifications': [],
                    'unreadChatsCount': 2
                }
            )
        self.assertEqual(res.status_code, 200)

    def test_invalid_auth_401(self):
        res = self.client.get(reverse('auth'), content_type="application/json")

        self.assertEqual(res.status_code, 401)
        self.assertEqual(res.data, {'detail': 'Учетные данные не были предоставлены.'})

    def test_invalid_token_auth_401_2(self):
        tokens = self.user.get_token()
        res = self.client.get(reverse('auth'), headers={"Authorization": f"Bearer {tokens.get('accessToken')[::-1]}"},
                              content_type="application/json")

        self.assertEqual(res.status_code, 401)
        self.assertEqual(res.data.get("detail"), 'Данный токен недействителен для любого типа токена')


class SendVerifyCodeViewTest(APITestCase):
    def setUp(self):
        self.unverified_user: CustomUser = CustomUser.objects.create_user(
            email="test@mail.com",
            password="test123",
            is_verified=False
        )

        self.verified_user: CustomUser = CustomUser.objects.create_user(
            email="test2@mail.com",
            password="test123",
            is_verified=True
        )

        self.active_code_user: CustomUser = CustomUser.objects.create_user(
            email="test3@mail.com",
            password="test123",

        )

        VerificationCode.objects.create(
            user=self.active_code_user,
            code=1234,
            type=VerificationCode.REGISTRATION_TYPE,
        )

    def test_rg_code_200(self):
        res = self.client.post(reverse('send_verify_code'), data=json.dumps({"email": "test@mail.com", "type": "RG"}),
                               content_type="application/json")

        VerificationCode.objects.get(user=self.unverified_user, type=VerificationCode.REGISTRATION_TYPE)

        self.assertEqual(res.data, {'message': 'Код подтверждения отправлен на электронную почту'})
        self.assertEqual(res.status_code, 200)

    def test_rg_user_already_verified_405(self):
        res = self.client.post(reverse('send_verify_code'), data=json.dumps({"email": "test2@mail.com", "type": "RG"}),
                               content_type="application/json")

        self.assertEqual(res.data, {'message': 'Пользователь уже верифицирован'})
        self.assertEqual(res.status_code, 405)

    def test_rg_user_not_found_405(self):
        res = self.client.post(reverse('send_verify_code'), data=json.dumps({"email": "wrong_email@mail.com",
                                                                             "type": "RG"}),
                               content_type="application/json")

        self.assertEqual(res.data, {'message': 'Пользователь не найден'})
        self.assertEqual(res.status_code, 404)

    def test_rg_code_still_active_409(self):
        res = self.client.post(reverse('send_verify_code'), data=json.dumps({"email": "test3@mail.com", "type": "RG"}),
                               content_type="application/json")

        self.assertEqual(res.data, {'message': 'Проверочный код по-прежнему активен, повторите попытку позже'})
        self.assertEqual(res.status_code, 409)

    def test_em_code_200(self):
        tokens = self.unverified_user.get_token()
        res = self.client.post(reverse('send_verify_code'),
                               data=json.dumps({
                                   "email": "change_email@mail.com",
                                   "type": "EM"}),
                               headers={"Authorization": f"Bearer {tokens.get('accessToken')}"},
                               content_type="application/json")

        self.assertEqual(res.data, {'message': 'Код подтверждения отправлен на электронную почту'})
        self.assertEqual(res.status_code, 200)

    def test_em_not_authenticated_401(self):
        res = self.client.post(reverse('send_verify_code'),
                               data=json.dumps({
                                   "email": "change_email@mail.com",
                                   "type": "EM"}),
                               content_type="application/json")

        self.assertEqual(res.data, {'message': 'Пользователь не авторизован'})
        self.assertEqual(res.status_code, 401)

    def test_pw_code_200(self):
        res = self.client.post(reverse('send_verify_code'),
                               data=json.dumps({
                                   "type": "PW",
                                   "email": "test2@mail.com"}),
                               content_type="application/json")

        self.assertEqual(res.data, {'message': 'Код подтверждения отправлен на электронную почту'})
        self.assertEqual(res.status_code, 200)

    def test_pw_user_not_found_404(self):
        res = self.client.post(reverse('send_verify_code'),
                               data=json.dumps({
                                   "type": "PW",
                                   "email": "test1232@mail.com"}),
                               content_type="application/json")

        self.assertEqual(res.data, {'message': 'Пользователь не найден'})
        self.assertEqual(res.status_code, 404)


    def test_incorrect_type_406(self):
        res = self.client.post(reverse('send_verify_code'),
                               data=json.dumps({
                                   "type": "PD",
                                   "email": "test2@mail.com"}),
                               content_type="application/json")

        self.assertEqual(res.data, {'message': 'Неверный тип кода'})
        self.assertEqual(res.status_code, 406)


class ChangePasswordViewTest(APITestCase):
    def setUp(self):
        self.user: CustomUser = CustomUser.objects.create_user(
            email="test@mail.com",
            password="test123",
            is_verified=True
        )

        tokens = self.user.get_token()
        self.access_token = tokens.get("accessToken")

        self.Vcode: VerificationCode = VerificationCode.objects.create(
            user=self.user, code=1234, type=VerificationCode.PASSWORD_CHANGE_TYPE,
        )

    def test_change_password_200(self):
        res = self.client.post(reverse('change_password'),
                               data=json.dumps({
                                   "code": 1234,
                                   "email": "test@mail.com",
                                   "new_password": "new_password",
                               }),
                               headers={"Authorization": f"Bearer {self.access_token}"},
                               content_type="application/json")

        user = CustomUser.objects.get(email="test@mail.com")

        self.assertEqual(res.data, {'message': 'Пароль был изменен'})
        self.assertEqual(res.status_code, 200)
        self.assertTrue(user.check_password("new_password"))

    def test_code_not_found_404(self):
        self.Vcode.is_used = True
        self.Vcode.save()

        res = self.client.post(reverse('change_password'),
                               data=json.dumps({
                                   "code": 1234,
                                   "email": "test@mail.com",
                                   "new_password": "new_password",
                               }),
                               headers={"Authorization": f"Bearer {self.access_token}"},
                               content_type="application/json")

        self.assertEqual(res.data, {'message': 'Проверочный код не найден или срок действия истек'})
        self.assertEqual(res.status_code, 404)

    def test_code_not_valid_404(self):
        self.Vcode.created_at = timezone.now() - timezone.timedelta(days=2)
        self.Vcode.save()

        res = self.client.post(reverse('change_password'),
                               data=json.dumps({
                                   "code": 1234,
                                   "email": "test@mail.com",
                                   "new_password": "new_password",
                               }),
                               headers={"Authorization": f"Bearer {self.access_token}"},
                               content_type="application/json")

        self.assertEqual(res.data, {'message': 'Проверочный код не найден или срок действия истек'})
        self.assertEqual(res.status_code, 404)

    def test_code_incorrect_406(self):
        res = self.client.post(reverse('change_password'),
                               data=json.dumps({
                                   "code": 1235,
                                   "email": "test@mail.com",
                                   "new_password": "new_password",
                               }),
                               headers={"Authorization": f"Bearer {self.access_token}"},
                               content_type="application/json")

        self.assertEqual(res.data, {'message': 'Неверный проверочный код'})
        self.assertEqual(res.status_code, 406)

    def test_user_not_found_409(self):
        res = self.client.post(reverse('change_password'),
                               data=json.dumps({
                                   "code": 1235,
                                   "email": "test2@mail.com",
                                   "new_password": "new_password",
                               }),
                               headers={"Authorization": f"Bearer {self.access_token}"},
                               content_type="application/json")

        self.assertEqual(res.data, {'message': 'Пользователь не найден'})
        self.assertEqual(res.status_code, 409)


class ChangeEmailViewTest(APITestCase):
    def setUp(self):
        self.user: CustomUser = CustomUser.objects.create_user(
            email="test@mail.com",
            password="test123",
            is_verified=True
        )

        tokens = self.user.get_token()
        self.access_token = tokens.get("accessToken")

        self.Vcode: VerificationCode = VerificationCode.objects.create(
            user=self.user, code=1234, type=VerificationCode.EMAIL_CHANGE_TYPE,
            new_email="new_email@mail.ru"
        )

    def test_change_password_200(self):
        res = self.client.post(reverse('change_email'),
                               data=json.dumps({
                                   "code": 1234,
                               }),
                               headers={"Authorization": f"Bearer {self.access_token}"},
                               content_type="application/json")

        user = CustomUser.objects.get(id=self.user.id)

        self.assertEqual(res.data, {'message': 'Адрес электронной почты был изменен'})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(user.email, "new_email@mail.ru")

    def test_code_not_found_404(self):
        self.Vcode.is_used = True
        self.Vcode.save()

        res = self.client.post(reverse('change_email'),
                               data=json.dumps({
                                   "code": 1234,
                               }),
                               headers={"Authorization": f"Bearer {self.access_token}"},
                               content_type="application/json")

        self.assertEqual(res.data, {'message': 'Проверочный код не найден или срок действия истек'})
        self.assertEqual(res.status_code, 404)

    #
    def test_code_not_valid_404(self):
        self.Vcode.created_at = timezone.now() - timezone.timedelta(days=2)
        self.Vcode.save()

        res = self.client.post(reverse('change_email'),
                               data=json.dumps({
                                   "code": 1234,
                               }),
                               headers={"Authorization": f"Bearer {self.access_token}"},
                               content_type="application/json")

        self.assertEqual(res.data, {'message': 'Проверочный код не найден или срок действия истек'})
        self.assertEqual(res.status_code, 404)

    #
    def test_code_incorrect_406(self):
        res = self.client.post(reverse('change_email'),
                               data=json.dumps({
                                   "code": 1235,
                               }),
                               headers={"Authorization": f"Bearer {self.access_token}"},
                               content_type="application/json")

        self.assertEqual(res.data, {'message': 'Неверный проверочный код'})
        self.assertEqual(res.status_code, 406)


