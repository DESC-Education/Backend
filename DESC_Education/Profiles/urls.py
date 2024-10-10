from django.urls import path

from Profiles.views import (
    ProfileView,
    GetMyProfileView,
    GetProfileView,
    UniversitiesList,
    SkillsList,
    CitiesList,
    FacultiesList,
    SpecialtiesList,
    ChangeLogoImgView,
    SendPhoneCodeView,
    SetPhoneView,
    EditProfileView,
    TestVerifyView,
    GenerateProfileReportView


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
    path('profile/my', GetMyProfileView.as_view(), name='profile_my'),
    path('profile/edit', EditProfileView.as_view(), name='profile_edit'),
    path('profile/<uuid:pk>', GetProfileView.as_view(), name='profile_get'),
    path('universities', UniversitiesList.as_view(), name='universities_list'),
    path('skills', SkillsList.as_view(), name='skills_list'),
    path('cities', CitiesList.as_view(), name='cities_list'),
    path('faculties', FacultiesList.as_view(), name='faculties_list'),
    path('specialties', SpecialtiesList.as_view(), name='specialties_list'),
    path('logo', ChangeLogoImgView.as_view(), name='logo_change'),
    path('phone/code', SendPhoneCodeView.as_view(), name='send_phone_code'),
    path('phone', SetPhoneView.as_view(), name='set_phone'),
    path('report', GenerateProfileReportView.as_view(), name='generate_report'),

    path('test_profile_verify', TestVerifyView.as_view(), name='test_verify')

]
