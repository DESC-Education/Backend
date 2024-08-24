from django.urls import path

from Tasks.views import (
    TaskView

)



urlpatterns = [
    path('task', TaskView.as_view(), name='task'),
    path('task/<uuid:pk>', TaskView.as_view(), name='task_edit'),


]
