from celery import shared_task
from Notifications.models import Notification
from Profiles.models import ProfileVerifyRequest
from django.core import serializers
from Notifications.serializers import NotificationSerializer, MessageNotificationSerializer
from django_eventstream import send_event
from Chats.models import ChatMembers, Message, Chat
from Chats.serializers import ChatSerializer
from django.db.models import Q
import time


@shared_task
def EventStreamSendNotification(instance_id, type):

    match type:
        case Notification.VERIFICATION_TYPE:
            instance = ProfileVerifyRequest.objects.get(id=instance_id)
            if instance.status not in [ProfileVerifyRequest.APPROVED, ProfileVerifyRequest.REJECTED]:
                return
            message_dict = {
                ProfileVerifyRequest.APPROVED: "Ваш профиль был подтвержден",
                ProfileVerifyRequest.REJECTED: "К сожалению, ваш профиль был отклонен."
            }

            notification = Notification.objects.create(
                user_id=instance.profile.user.id,
                message=message_dict[instance.status],
                type=Notification.VERIFICATION_TYPE,
                title="Верификация профиля"
            )
            serializer = NotificationSerializer(notification)
            send_event(f"user-{instance.profile.user.id}", 'notification', serializer.data)


@shared_task
def EventStreamSendNotifyNewMessage(message_id):
    instance = Message.objects.get(id=message_id)
    chat_member = ChatMembers.objects.filter(~Q(user=instance.user) & Q(chat=instance.chat)).first()
    if chat_member:
        user = chat_member.user
        serializer = MessageNotificationSerializer(instance, data={'user': user.id})
        serializer.is_valid()
        print(user.id)
        send_event(f"user-{user.id}", 'newMessage', serializer.data)


@shared_task
def EventStreamSendNotifyNewChat(new_chat_id, user_id):
    instance = Chat.objects.get(id=new_chat_id)
    chat_member = ChatMembers.objects.filter(~Q(user_id=user_id) & Q(chat=instance)).first()
    if chat_member:
        # user = chat_member.user
        # serializer = ChatSerializer(instance)
        # serializer.is_valid()
        # serializer.save(user=user)
        # print(serializer.data)
        send_event(f"user-{user.id}", 'newMessage', serializer.data)
