from django.urls import path

from Tasks.views import (
    TaskView,
    TaskDetailView

)



urlpatterns = [
    path('task', TaskView.as_view(), name='task'),
    path('task/<uuid:pk>', TaskDetailView.as_view(), name='task_edit'),


]
