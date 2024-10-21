from django.urls import path
from Admins.views import (
    AdminProfileVerifyRequestListView,
    AdminProfileVerifyRequestDetailView,
    AdminCustomUserListView,
    AdminCustomUserDetailView,
    StatisticsUserView

)



urlpatterns = [
    path('profile/requests', AdminProfileVerifyRequestListView.as_view(), name='admin_v_request_list'),
    path('profile/request/<uuid:pk>', AdminProfileVerifyRequestDetailView.as_view(), name='admin_v_request_detail'),
    path('users/', AdminCustomUserListView.as_view(), name='admin_user_list'),
    path('user/<uuid:pk>', AdminCustomUserDetailView.as_view(), name='admin_user_detail'),


    path('stats/users', StatisticsUserView.as_view(), name='stats_users'),

]
