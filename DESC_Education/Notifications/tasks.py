import json

from celery import shared_task
from django.apps import apps
from Notifications.models import Notification
from django.core import serializers
from Notifications.serializers import NotificationSerializer, MessageNotificationSerializer
from django_eventstream import send_event
from Chats.models import ChatMembers, Message, Chat
from Chats.serializers import ChatSerializer
from django.db.models import Q
from django.http.request import HttpRequest
from Tasks.models import Solution, Review
from Tasks.serializers import SolutionSerializer, ReviewSerializer
from Chats.serializers import ChatDetailSerializer, ChatListSerializer
import time
from Users.models import CustomUser

ProfileVerifyRequest = apps.get_model('Profiles', 'ProfileVerifyRequest')


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
            send_event(f"user-{str(instance.profile.user.id)}", 'notification', serializer.data)

        case Notification.EVALUATION_TYPE:
            instance = Solution.objects.get(id=instance_id)
            if instance.status not in [Solution.FAILED, Solution.COMPLETED]:
                return
            message_dict = {
                Solution.FAILED: f"Ваше рещение по заданию {instance.task.title} было оценено как не выполненое.",
                Solution.COMPLETED: f"Ваше рещение по заданию {instance.task.title} было оценено как успешно выполненое."
            }
            solution_serializer = dict(SolutionSerializer(instance).data)
            solution_serializer['user'] = str(solution_serializer['user'])

            notification = Notification.objects.create(
                user=instance.user,
                message=message_dict[instance.status],
                type=Notification.EVALUATION_TYPE,
                title="Ваше решение оценено",
                payload=solution_serializer
            )

            serializer = NotificationSerializer(notification)
            send_event(f"user-{str(instance.user.id)}", 'notification', serializer.data)

        case Notification.SOLUTION_TYPE:
            instance = Solution.objects.get(id=instance_id)

            solution_serializer = dict(SolutionSerializer(instance).data)
            solution_serializer['user'] = str(solution_serializer['user'])

            notification = Notification.objects.create(
                user=instance.task.user,
                message=f"Добавлено новое решение по вашему заданию {instance.task.title}",
                type=Notification.SOLUTION_TYPE,
                title="Новое решение",
                payload=solution_serializer
            )

            serializer = NotificationSerializer(notification)

            send_event(f"user-{str(instance.task.user.id)}", 'notification', serializer.data)

        case Notification.REVIEW_TYPE:
            instance = Review.objects.get(id=instance_id)
            solution_serializer = dict(SolutionSerializer(instance.solution).data)
            solution_serializer['user'] = str(solution_serializer['user'])
            solution_serializer['review']['solution'] = str(solution_serializer['review']['solution'])

            notification = Notification.objects.create(
                user=instance.solution.user,
                message=f"Вам оставили новый отзыв по вашему решению: {instance.solution.task.title}",
                type=Notification.REVIEW_TYPE,
                title="Новый отзыв",
                payload=solution_serializer
            )
            serializer = NotificationSerializer(notification)

            send_event(f"user-{str(instance.solution.user.id)}", 'notification', serializer.data)

        case Notification.COUNT_RESET_TYPE:
            instance = CustomUser.objects.get(id=instance_id)

            notification = Notification.objects.create(
                user=instance,
                message=f"Ваше количество откликов пополнено",
                type=Notification.COUNT_RESET_TYPE,
                title="Ежемесячное пополнение откликов",
            )

            serializer = NotificationSerializer(notification)

            send_event(f"user-{str(instance.id)}", 'notification', serializer.data)

        case Notification.LEVEL_TYPE:
            instance = CustomUser.objects.get(id=instance_id)
            profile = instance.get_profile()

            notification = Notification.objects.create(
                user=instance,
                message=f'Ваш уровень повышен до "{profile.get_level_id_display()}"',
                type=Notification.LEVEL_TYPE,
                title="Повышение уровня",
                payload={
                    'value': profile.level_id,
                    'name': profile.get_level_id_display(),
                }
            )

            serializer = NotificationSerializer(notification)

            send_event(f"user-{str(instance.id)}", 'notification', serializer.data)

        case Notification.VIEWED_TYPE:
            instance = Message.objects.get(id=instance_id)

            chat_members = ChatMembers.objects.filter(Q(chat=instance.chat))
            for member in chat_members:
                user = member.user
                serializer = MessageNotificationSerializer(instance, data={'user': str(user.id)})
                serializer.is_valid()

                send_event(f"user-{user.id}", 'viewed', serializer.data)









@shared_task
def EventStreamSendNotifyNewMessage(message_id):
    instance = Message.objects.get(id=message_id)
    count_messages = instance.chat.messages.count()

    chat_member = ChatMembers.objects.filter(~Q(user=instance.user) & Q(chat=instance.chat)).first()
    if not chat_member:
        return
    user = chat_member.user

    if count_messages == 1:
        req = HttpRequest()
        req.user = user
        context = {'request': req}
        serializer = ChatListSerializer(instance.chat, context=context)
        send_event(f"user-{user.id}", 'newChat', serializer.data)
    else:
        serializer = MessageNotificationSerializer(instance, data={'user': user.id})
        serializer.is_valid()
        send_event(f"user-{user.id}", 'newMessage', serializer.data)
