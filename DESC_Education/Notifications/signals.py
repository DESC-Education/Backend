from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from Notifications.models import Notification
from Notifications.serializers import NotificationSerializer, MessageNotificationSerializer
from Profiles.models import StudentProfile, CompanyProfile, ProfileVerifyRequest
from Tasks.models import Solution
from django_eventstream import send_event
from Chats.models import Message, Chat, ChatMembers
from django.db.models import Q
from Notifications.tasks import EventStreamSendNotification, EventStreamSendNotifyNewMessage
import time
from django.core import serializers


@receiver(post_save, sender=ProfileVerifyRequest)
def notify_student_profile_verification(sender, instance: ProfileVerifyRequest, **kwargs):
    EventStreamSendNotification.delay(instance.id, Notification.VERIFICATION_TYPE)


@receiver(post_save, sender=Message)
def notify_new_message(sender, instance: Message, created, **kwargs):
    EventStreamSendNotifyNewMessage.delay(instance.id)
