from django_filters import rest_framework as drf_filters
from Tasks.models import Task, Filter, TaskCategory


class TaskFilter(drf_filters.FilterSet):
    filters = drf_filters.ModelMultipleChoiceFilter(queryset=Filter.objects.all(), field_name='filters')
    category = drf_filters.ModelChoiceFilter(queryset=TaskCategory.objects.all(), field_name='category')

    class Meta:
        model = Task
        fields = ['filters', 'category']
