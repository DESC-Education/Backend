from django.urls import path

from Profiles.views import (
    CreateProfileView
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
    path('profile', CreateProfileView.as_view(), name='profile_create'),


]
