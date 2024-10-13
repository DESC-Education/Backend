from celery import shared_task
from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.conf import settings
import os
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.template import Context
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.utils.html import strip_tags


@shared_task
def MailVerifyRegistration(email, code):
    html_content = render_to_string('reg_mail.html', {'code': code})

    msg = EmailMessage(
        "Подтверждение регистрации", html_content, settings.DEFAULT_FROM_EMAIL, [email]
    )
    msg.content_subtype = 'html'
    msg.send()

@shared_task
def MailProfileVerification(email, verified, comment):

    if verified:
        verified_text = "Ваш профиль был подтвержден!"
        html_content = render_to_string('approved.html')
    else:
        verified_text = "Ваш профиль был отклонен!"
        html_content = render_to_string('rejected.html', {'comment': comment})

    msg = EmailMessage(
        verified_text, html_content, settings.DEFAULT_FROM_EMAIL, [email]
    )
    msg.content_subtype = 'html'
    msg.send()


@shared_task
def MailChangeMail(email, code):
    html_content = render_to_string('mail_code.html', {'code': code})

    msg = EmailMessage(
        "Смена почты", html_content, settings.DEFAULT_FROM_EMAIL, [email]
    )
    msg.content_subtype = 'html'
    msg.send()

@shared_task
def MailChangePassword(email, code):
    html_content = render_to_string('pass_code.html', {'code': code})

    msg = EmailMessage(
        "Смена пароля", html_content, settings.DEFAULT_FROM_EMAIL, [email]
    )
    msg.content_subtype = 'html'
    msg.send()