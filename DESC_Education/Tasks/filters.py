
from rest_framework.filters import BaseFilterBackend







class CategoryFilterBackend(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        taskCategoryId = request.query_params.get('taskCategoryId')
        if taskCategoryId:
            queryset = queryset.filter(task_categories__id=taskCategoryId)
        return queryset