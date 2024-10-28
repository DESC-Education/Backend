from django.urls import path
from Admins.views import (
    AdminProfileVerifyRequestListView,
    AdminProfileVerifyRequestDetailView,
    AdminCustomUserListView,
    AdminCustomUserDetailView,
    StatisticsUserView,
    StatisticsTasksView,
    AdminUserChatsListView,
    AdminCompanyTasksListView,
    AdminStudentSolutionsListView,
    AdminTaskCategoryListView,
    AdminTaskCategoryDetailView

)



urlpatterns = [
    path('profile/requests', AdminProfileVerifyRequestListView.as_view(), name='admin_v_request_list'),
    path('profile/request/<uuid:pk>', AdminProfileVerifyRequestDetailView.as_view(), name='admin_v_request_detail'),
    path('users/', AdminCustomUserListView.as_view(), name='admin_user_list'),
    path('user/<uuid:pk>', AdminCustomUserDetailView.as_view(), name='admin_user_detail'),
    path('user/<uuid:pk>/chats', AdminUserChatsListView.as_view(), name='admin_user_chats'),
    path('company/<uuid:pk>/tasks', AdminCompanyTasksListView.as_view(), name='admin_company_tasks'),
    path('student/<uuid:pk>/solutions', AdminStudentSolutionsListView.as_view(), name='admin_student_solutions'),


    path('taskCategory/list', AdminTaskCategoryListView.as_view(), name='task_category_list'),
    path('taskCategory/<uuid:pk>', AdminTaskCategoryDetailView.as_view(), name='task_category_list'),



    path('stats/users', StatisticsUserView.as_view(), name='stats_users'),
    path('stats/tasks', StatisticsTasksView.as_view(), name='stats_tasks'),

]
