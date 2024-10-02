from django.shortcuts import render
from django_eventstream import send_event
from django_eventstream.viewsets import EventsViewSet
from rest_framework.response import Response
from rest_framework import generics
from Settings.permissions import IsAuthenticatedAndVerified
from Notifications.models import Notification
from Notifications.serializers import NotificationSerializer


# Create your views here.


class Test(generics.GenericAPIView):
    def get(self, request, user_id, *args, **kwargs):
        send_event(f"user-{user_id}", 'message', {"message": "Hello, world!"})
        return Response(200)


class NotificationListView(generics.ListAPIView):
    permission_classes = [IsAuthenticatedAndVerified]
    serializer_class = NotificationSerializer

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)

    def get(self, *args, **kwargs):
        return super().get(*args, **kwargs)


class EventsUser(EventsViewSet):
    permission_classes = [IsAuthenticatedAndVerified]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)

    def list(self, request):
        user = request.user
        self.channels = [f"user-{user.id}"]
        return super().list(request)
