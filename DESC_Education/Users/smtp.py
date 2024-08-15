from django.conf import settings
from django.core.mail import EmailMessage


def send_auth_registration_code(email, code):
    msg = EmailMessage(
        'Подтверждение регистрации',
        f'Ваш код для подтверждения регистрации: {code}',
        to=[email]
    )
    msg.send()


def send_password_change_code(email, code):
    msg = EmailMessage(
        'Смена пароля',
        f'Ваш код для подтверждения смены пароля: {code}',
        to=[email]
    )
    msg.send()


def send_mail_change_code(email, code):
    msg = EmailMessage(
        'Смена почты',
        f'Ваш код для подтверждения смены почты: {code}',
        to=[email]
    )
    msg.send()
