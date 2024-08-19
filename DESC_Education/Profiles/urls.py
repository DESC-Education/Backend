from django.urls import path

from Profiles.views import (
    CreateStudentProfileView,
    CreateCompanyProfileView
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
    path('student_profile/create', CreateStudentProfileView.as_view(), name='student_profile_create'),
    path('company_profile/create', CreateCompanyProfileView.as_view(), name='company_profile_create'),

]
