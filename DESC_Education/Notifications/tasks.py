from celery import shared_task
from Notifications.models import Notification
from Profiles.models import ProfileVerifyRequest
from django.core import serializers
from Notifications.serializers import NotificationSerializer, MessageNotificationSerializer
from django_eventstream import send_event
from Chats.models import ChatMembers, Message, Chat
from Chats.serializers import ChatSerializer
from django.db.models import Q
from django.http.request import HttpRequest
from Tasks.models import Solution
from Chats.serializers import ChatDetailSerializer, ChatListSerializer
import time
from Users.models import CustomUser


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
                user=instance.profile.user,
                message=message_dict[instance.status],
                type=Notification.VERIFICATION_TYPE,
                title="Верификация профиля"
            )
            serializer = NotificationSerializer(notification)
            send_event(f"user-{instance.profile.user.id}", 'notification', serializer.data)

        case Notification.SOLUTION_TYPE:
            instance = Solution.objects.get(id=instance_id)
            if instance.status not in [Solution.FAILED, Solution.COMPLETED]:
                return
            message_dict = {
                Solution.FAILED: f"Ваше рещение по заданию {instance.task.title} было оценено как не выполненое.",
                Solution.COMPLETED: f"Ваше рещение по заданию {instance.task.title} было оценено как успешно выполненое."
            }

            notification = Notification.objects.create(
                user=instance.user,
                message=message_dict[instance.status],
                type=Notification.SOLUTION_TYPE,
                title="Ваше решение оценено",
                payload={'solutionId': str(instance.id),
                         'taskId': str(instance.task.id)}

            )

            serializer = NotificationSerializer(notification)
            send_event(f"user-{instance.user.id}", 'notification', serializer.data)





@shared_task
def EventStreamSendNotifyNewMessage(message_id):
    type = 'newMessage'
    instance = Message.objects.get(id=message_id)
    count_messages = instance.chat.messages.count()
    if count_messages == 1:
        type = 'newChat'

    chat_member = ChatMembers.objects.filter(~Q(user=instance.user) & Q(chat=instance.chat)).first()
    if not chat_member:
        return
    user = chat_member.user
    match type:
        case 'newMessage':
            serializer = MessageNotificationSerializer(instance, data={'user': user.id})
            serializer.is_valid()
            send_event(f"user-{user.id}", 'newMessage', serializer.data)
        case 'newChat':
            req = HttpRequest()
            req.user = user
            context = {'request': req}
            serializer = ChatListSerializer(instance.chat, context=context)
            send_event(f"user-{user.id}", 'newMessage', serializer.data)




