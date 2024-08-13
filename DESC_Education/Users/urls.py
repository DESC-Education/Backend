from django.urls import path
from django.contrib import admin
from Users.views import (
    LoginView,
    RegistrationView,
    HelloView
)


urlpatterns = [

    # path('admin/', admin.site.urls),
    path('api/login/', LoginView.as_view(), name='login'),
    path('api/register/', RegistrationView.as_view(), name='register'),
    # path('', HelloView.as_view(), name='hello'),

]
