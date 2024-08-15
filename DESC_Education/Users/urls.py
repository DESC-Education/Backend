from django.urls import path
from django.contrib import admin

from Users.views import (
    LoginView,
    RegistrationView,
    CustomTokenRefreshView,
    VerifyRegistrationView,
    AuthView,
    SendVerifyCodeView,

)



urlpatterns = [

    # path('admin/', admin.site.urls)
    path('login/', LoginView.as_view(), name='login'),
    path('registration/', RegistrationView.as_view(), name='registration'),
    path('token_refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
    path('registration/verify/', VerifyRegistrationView.as_view(), name='verify_registration'),
    path('auth/', AuthView.as_view(), name='auth'),
    path('send_verify_code/', SendVerifyCodeView.as_view(), name='send_verify_code'),


    # path('', HelloView.as_view(), name='hello'),

]
