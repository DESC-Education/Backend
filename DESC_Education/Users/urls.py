from django.urls import path
from django.contrib import admin

from Users.views import (
    LoginView,
    RegistrationView,
    HelloView,
    CustomTokenRefreshView,
    VerifyRegistrationView

)


urlpatterns = [

    # path('admin/', admin.site.urls),
    path('login/', LoginView.as_view(), name='login'),
    path('registration/', RegistrationView.as_view(), name='registration'),
    path('token_refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
    path('register/verify', VerifyRegistrationView.as_view(), name='verify_registration'),

    # path('', HelloView.as_view(), name='hello'),

]
