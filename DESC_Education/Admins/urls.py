from django.urls import path
from Admins.views import (
    AdminProfileVerifyRequestsView,
    AdminProfileVerifyRequestDetailView,
)



urlpatterns = [
    path('profile/requests', AdminProfileVerifyRequestsView.as_view(), name='admin_v_request_list'),
    path('profile/request/<uuid:pk>', AdminProfileVerifyRequestDetailView.as_view(), name='admin_v_request_detail')

]
