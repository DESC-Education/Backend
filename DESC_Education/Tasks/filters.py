import attrs
from django_filters import rest_framework as drf_filters
from Tasks.models import Task, Filter, TaskCategory


class TaskFilter(drf_filters.FilterSet):
    filters = drf_filters.ModelMultipleChoiceFilter(queryset=Filter.objects.all(), field_name='filters')
    category = drf_filters.ModelChoiceFilter(queryset=TaskCategory.objects.all(), field_name='category')

    ordering = drf_filters.OrderingFilter(
        fields=(
            ('created_at', 'createdAt'),
        ),

        # labels do not need to retain order
        field_labels={
            'created_at': 'По дате добавления',
        }

    )


    class Meta:
        model = Task
        fields = ['filters', 'category']
