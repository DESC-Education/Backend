from django.urls import path
from Admins.views import AdminProfileVerifyRequestsView



urlpatterns = [
    path('profile/requests', AdminProfileVerifyRequestsView.as_view(), name='v_request_list')

]
