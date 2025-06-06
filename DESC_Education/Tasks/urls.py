from django.urls import path

from Tasks.views import (
    TaskView,
    TaskDetailView,
    TaskListView,
    SolutionView,
    SolutionListView,
    SolutionDetailView,
    TaskCategoryListView,
    CompanyTasksMyView,
    StudentTasksMyView,
    TaskPatternPatternListView,
    EvaluateSolutionView,
    ReviewCreateView,
    ReviewListView,


)



urlpatterns = [
    path('task', TaskView.as_view(), name='task'),
    path('tasks', TaskListView.as_view(), name='get_tasks'),
    path('task/<uuid:pk>', TaskDetailView.as_view(), name='task_detail'),
    path('task/evaluate/<uuid:pk>', EvaluateSolutionView.as_view(), name='task_evaluate'),
    path('solution', SolutionView.as_view(), name='solution'),
    path('solution-list/<uuid:pk>', SolutionListView.as_view(), name='solution-list-by-task'),
    path('solution/<uuid:pk>', SolutionDetailView.as_view(), name='solution_detail'),
    path('solution/review', ReviewCreateView.as_view(), name='review_create'),
    path('review-list', ReviewListView.as_view(), name='review_list'),
    path('task/categories', TaskCategoryListView.as_view(), name='task_category_list'),
    path('my/company', CompanyTasksMyView.as_view(), name='company_tasks_my'),
    path('my/student', StudentTasksMyView.as_view(), name='student_tasks_my'),
    path('patterns', TaskPatternPatternListView.as_view(), name='task_pattern_list'),






]
