from django.urls import path
from Admins.views import (
    AdminProfileVerifyRequestListView,
    AdminProfileVerifyRequestDetailView,
    AdminCustomUserListView,
    AdminCustomUserDetailView,
    StatisticsUserView,
    StatisticsTasksView,
    AdminUserChatsListView

)



urlpatterns = [
    path('profile/requests', AdminProfileVerifyRequestListView.as_view(), name='admin_v_request_list'),
    path('profile/request/<uuid:pk>', AdminProfileVerifyRequestDetailView.as_view(), name='admin_v_request_detail'),
    path('users/', AdminCustomUserListView.as_view(), name='admin_user_list'),
    path('user/<uuid:pk>', AdminCustomUserDetailView.as_view(), name='admin_user_detail'),
    path('user/<uuid:pk>/chats', AdminUserChatsListView.as_view(), name='admin_user_chats'),



    path('stats/users', StatisticsUserView.as_view(), name='stats_users'),
    path('stats/tasks', StatisticsTasksView.as_view(), name='stats_tasks'),

]
