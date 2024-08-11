from django.urls import path
from django.contrib import admin
from Auth_API.views import (
    LoginView,
    HelloView
)


urlpatterns = [

    # path('admin/', admin.site.urls),
    path('api/login/', LoginView.as_view(), name='login'),
    path('', HelloView.as_view(), name='hello'),

]
