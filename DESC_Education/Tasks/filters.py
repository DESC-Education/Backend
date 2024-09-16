import attrs
from django_filters import rest_framework as drf_filters
from Tasks.models import Task, Filter, TaskCategory, Solution
from django.utils import timezone
from django.db.models import Q


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


class MyTasksFilter(drf_filters.FilterSet):
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
        fields = []


class SolutionFilter(drf_filters.FilterSet):
    ordering = drf_filters.OrderingFilter(
        fields=(
            ('created_at', 'createdAt'),
        ),

        # labels do not need to retain order
        field_labels={
            'created_at': 'По дате добавления',
        }

    )

    status = drf_filters.ChoiceFilter(choices=Solution.STATUSES, field_name='status')

    class Meta:
        model = Solution
        fields = ['status']