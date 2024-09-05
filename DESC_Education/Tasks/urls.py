from django.urls import path

from Tasks.views import (
    TaskView,
    TaskDetailView,
    TaskListView,
    SolutionView,
    SolutionDetailView,
    TaskCategoryListView,
    CompanyTasksMyView,
    StudentTasksMyView,
    TaskPatternPatternListView,
    EvaluateSolutionView


)



urlpatterns = [
    path('task', TaskView.as_view(), name='task'),
    path('tasks', TaskListView.as_view(), name='get_tasks'),
    path('task/<uuid:pk>', TaskDetailView.as_view(), name='task_detail'),
    path('task/evaluate/<uuid:pk>', EvaluateSolutionView.as_view(), name='task_evaluate'),
    path('solution', SolutionView.as_view(), name='solution'),
    path('solution/<uuid:pk>', SolutionDetailView.as_view(), name='solution_detail'),
    path('task/categories', TaskCategoryListView.as_view(), name='task_category_list'),
    path('my/company', CompanyTasksMyView.as_view(), name='company_tasks_my'),
    path('my/student', StudentTasksMyView.as_view(), name='student_tasks_my'),
    path('patterns', TaskPatternPatternListView.as_view(), name='task_pattern_list'),





]
