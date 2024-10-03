from celery import shared_task
from Notifications.models import Notification
from Profiles.models import ProfileVerifyRequest
from django.core import serializers




@shared_task
def EventStreamSendNotification(serialized_instance, type):
    instance = serializers.deserialize('json', serialized_instance)
    match type:
        case Notification.VERIFICATION_TYPE:
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

