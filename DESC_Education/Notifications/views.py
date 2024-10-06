from django.shortcuts import render
from django_eventstream import send_event
from django_eventstream.viewsets import EventsViewSet
from rest_framework.response import Response
from rest_framework import generics
from Settings.permissions import IsAuthenticatedAndVerified
from Notifications.models import Notification
from Notifications.serializers import NotificationSerializer
from rest_framework import status
from django.utils import timezone
from drf_spectacular.utils import extend_schema


# Create your views here.


class Test(generics.GenericAPIView):
    def get(self, request, user_id, *args, **kwargs):
        send_event(f"user-{user_id}", 'message', {"message": "Hello, world!"})
        return Response(200)


class NotificationListView(generics.ListAPIView):
    permission_classes = [IsAuthenticatedAndVerified]
    serializer_class = NotificationSerializer

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user,
                                           created_at__gte=(timezone.now() - timezone.timedelta(days=7)))

    @extend_schema(
        tags=["Notifications"],
        summary="Получение списка уведомлений",
    )
    def get(self, *args, **kwargs):
        return super().get(*args, **kwargs)


class EventsUser(EventsViewSet):
    permission_classes = [IsAuthenticatedAndVerified]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)

    @extend_schema(
        tags=["Notifications"],
        summary="Подключение к sse уведомлений",
    )
    def list(self, request):
        user = request.user
        self.channels = [f"user-{user.id}"]
        return super().list(request)


class ReadNotificationView(generics.GenericAPIView):
    permission_classes = [IsAuthenticatedAndVerified]

    def get_object(self) -> Notification:
        instance = generics.get_object_or_404(Notification, pk=self.kwargs.get('pk'))
        if self.request.user != instance.user:
            return Response(status=status.HTTP_404_NOT_FOUND)

        return instance

    @extend_schema(
        tags=["Notifications"],
        summary="Отметка о прочтении сообщения",
    )
    def get(self, request, pk, *args, **kwargs):
        instance = self.get_object()
        instance.is_read = True
        instance.save()
        serializer = NotificationSerializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)
