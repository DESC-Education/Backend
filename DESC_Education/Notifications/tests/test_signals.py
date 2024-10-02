from django.test import TestCase
from Notifications.models import Notification
from Users.models import CustomUser
from Profiles.models import StudentProfile, ProfileVerifyRequest
from django.urls import reverse
from asgiref.sync import async_to_sync
import asyncio
from django_eventstream import send_event
from channels.testing import WebsocketCommunicator




class NotifyProfileVerificationTest(TestCase):
    def setUp(self):
        self.student = CustomUser.objects.create_user(
            email='example@example.com',
            password='password',
            role=CustomUser.STUDENT_ROLE,
            is_verified=True
        )

        self.company = CustomUser.objects.create_user(
            email='example2@example.com',
            password='password',
            role=CustomUser.COMPANY_ROLE,
            is_verified=True
        )


    def base_test(self, user):
        profile = user.get_profile()
        req = ProfileVerifyRequest.objects.create(profile=profile)
        req.status = ProfileVerifyRequest.APPROVED
        req.save()

        post_notifications = Notification.objects.filter(user=user)

        notification = post_notifications.first()
        self.assertEqual(post_notifications.count(), 1)
        self.assertEqual(notification.user.id, user.id)
        self.assertEqual(notification.message, 'Ваш профиль был подтвержден')

        req.status = ProfileVerifyRequest.PENDING
        req.save()
        req.status = ProfileVerifyRequest.REJECTED
        req.save()

        post_notifications = Notification.objects.filter(user=user)

        notification = post_notifications.first()
        self.assertEqual(post_notifications.count(), 2)
        self.assertEqual(notification.user.id, user.id)
        self.assertEqual(notification.message, 'К сожалению, ваш профиль был отклонен.')




    def test_student_signal(self):
        self.base_test(self.student)
        self.base_test(self.company)
