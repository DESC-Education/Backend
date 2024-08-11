from django.conf import settings
from django.core.mail import send_mail





def auth_register_mail(mail):

    send_mail('Тема', 'Тело письма', settings.EMAIL_HOST_USER, [mail])

