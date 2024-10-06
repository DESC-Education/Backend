from django.urls import path, include
from django_eventstream import urls
from Notifications.views import Test, EventsUser, NotificationListView, ReadNotificationView

urlpatterns = [
    path('events', EventsUser.as_view({'get': 'list'}), name='events'),
    path('notifications', NotificationListView.as_view(), name='get_notifications'),
    path('notification/read/<uuid:pk>', ReadNotificationView.as_view(), name='read_notification'),

    # path('events', include(urls), {"channels": ["test"]}, name='events'),
    path('test/<uuid:user_id>', Test.as_view(), name='test')
]
