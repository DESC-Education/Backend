from django.urls import path

from Profiles.views import (
    ProfileView,
    GetMyProfileView,
    GetProfileView,
    testView,
)
# from Users.views import (
#     LoginView,
#     RegistrationView,
#     CustomTokenRefreshView,
#     VerifyRegistrationView,
#     AuthView,
#     SendVerifyCodeView,
#     ChangePasswordView,
#     ChangeEmailView
#
# )



urlpatterns = [
    path('profile', ProfileView.as_view(), name='profile_create'),
    path('test', testView.as_view(), name='test'),
    path('profile/my', GetMyProfileView.as_view(), name='profile_my'),
    path('profile/<uuid:pk>', GetProfileView.as_view(), name='profile_get'),


]
