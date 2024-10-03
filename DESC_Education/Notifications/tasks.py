from celery import shared_task
from Notifications.models import Notification
from Profiles.models import ProfileVerifyRequest
from django.core import serializers




@shared_task
def EventStreamSendNotification(data, type):
    user_id = data.get('user_id')
    notification_status = data.get('notification_status')
    match type:
        case Notification.VERIFICATION_TYPE:
            message_dict = {
                ProfileVerifyRequest.APPROVED: "Ваш профиль был подтвержден",
                ProfileVerifyRequest.REJECTED: "К сожалению, ваш профиль был отклонен."
            }

            notification = Notification.objects.create(
                user_id=user_id,
                message=message_dict[notification_status],
                type=Notification.VERIFICATION_TYPE,
                title="Верификация профиля"
            )
            serializer = NotificationSerializer(notification)
            send_event(f"user-{user_id}", 'notification', serializer.data)

