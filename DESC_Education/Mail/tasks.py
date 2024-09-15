from celery import shared_task
from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.conf import settings
import os
# from pybars import Compiler
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.template import Context
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.utils.html import strip_tags

@shared_task
def send_auth_registration_code(email, code):

    html_content = render_to_string('reg.html', {'code': code})
    text_content = strip_tags(html_content)

    msg = EmailMultiAlternatives(
        "Подтверждение регистрации", html_content, settings.DEFAULT_FROM_EMAIL, [email]
    )
    msg.content_subtype = 'html'
    # msg.attach_alternative(html_content, "text/html")
    msg.send()