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
    path('profile/', GetMyProfileView.as_view(), name='profile_my'),
    path('profile/<uuid:pk>', GetProfileView.as_view(), name='profile_get'),
    path('profile/universities', UniversitiesList.as_view(), name='universities_list'),
    path('profile/skills', SkillsList.as_view(), name='skills_list'),
    path('profile/cities', CitiesList.as_view(), name='cities_list'),
    path('profile/faculties', FacultiesList.as_view(), name='faculties_list'),
    path('profile/specialties', SpecialtiesList.as_view(), name='specialties_list'),
    path('profile/logo', ChangeLogoImgView.as_view(), name='logo_change'),
    path('profile/phone/code', SendPhoneCodeView.as_view(), name='send_phone_code'),

]
