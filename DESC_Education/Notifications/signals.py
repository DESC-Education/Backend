from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from Notifications.models import Notification
from Notifications.serializers import NotificationSerializer, MessageNotificationSerializer
from Profiles.models import StudentProfile, CompanyProfile, ProfileVerifyRequest
from Tasks.models import Solution
from django_eventstream import send_event
from Chats.models import Message, Chat, ChatMembers
from django.db.models import Q


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
            message_dict = {
                ProfileVerifyRequest.APPROVED: "Ваш профиль был подтвержден",
                ProfileVerifyRequest.REJECTED: "К сожалению, ваш профиль был отклонен."
            }


            notification = Notification.objects.create(
                user=instance.profile.user,
                message=message_dict[instance.status],
                type=Notification.VERIFICATION_TYPE,
                title="Проверка профиля"
            )
            serializer = NotificationSerializer(notification)
            send_event(f"user-{instance.profile.user.id}", 'notification', serializer.data)



@receiver(post_save, sender=Message)
def notify_new_message(sender, instance: Message, created, **kwargs):
    chatmember = instance.chat.chatmembers_set.filter(~Q(user=instance.user), Q(chat=instance.chat)).first()
    if chatmember:
        user = chatmember.user
        serializer = MessageNotificationSerializer(instance, data={'user': user.id})
        serializer.is_valid()
        send_event(f"user-{user.id}", 'newMessage', serializer.data)




