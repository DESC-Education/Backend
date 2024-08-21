from django.urls import path

from Profiles.views import (
    ProfileView,
    GetMyProfileView,
    GetProfileView,
    UniversitiesList,
    SkillsList,
    CityList,

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
    path('profile/cities', CityList.as_view(), name='cities_list'),



]
