from django.urls import path

from Profiles.views import (
    CreateStudentProfileView
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


    path('student_profile/create', CreateStudentProfileView.as_view(), name='student_profile'),


]
