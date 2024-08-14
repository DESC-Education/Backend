from django.conf import settings
from django.core.mail import EmailMessage



def send_auth_registration_code(email, code):
    msg = EmailMessage(
        'Подтверждение регистрации',
        f'Ваш код для подтверждения регистрации: {code}',
        to=[email]
    )

