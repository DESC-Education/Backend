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


@receiver(pre_save, sender=ProfileVerifyRequest)
def notify_student_profile_verification(sender, instance: ProfileVerifyRequest, **kwargs):
    try:
        obj: ProfileVerifyRequest = sender.objects.get(pk=instance.pk)
    except sender.DoesNotExist:
        pass
    else:
        if obj.status == ProfileVerifyRequest.PENDING \
                and instance.status in [ProfileVerifyRequest.REJECTED,
                                        ProfileVerifyRequest.APPROVED]:

            data = {
                "user_id": instance.profile.user.id,
                "notification_status": instance.status
            }
            EventStreamSendNotification.delay(data, Notification.VERIFICATION_TYPE)




@receiver(post_save, sender=Message)
def notify_new_message(sender, instance: Message, created, **kwargs):
    EventStreamSendNotifyNewMessage.delay(instance.id)



