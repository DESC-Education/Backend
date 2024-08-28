from django.urls import path

from Tasks.views import (
    TaskView,
    TaskDetailView,
    TaskListView,


)



urlpatterns = [
    path('task', TaskView.as_view(), name='task'),
    path('tasks', TaskListView.as_view(), name='get_tasks'),
    path('task/<uuid:pk>', TaskDetailView.as_view(), name='task_detail'),



]
