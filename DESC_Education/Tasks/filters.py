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


class CompanyMyTasksFilter(drf_filters.FilterSet):
    ordering = drf_filters.OrderingFilter(
        fields=(
            ('created_at', 'createdAt'),
        ),

        # labels do not need to retain order
        field_labels={
            'created_at': 'По дате добавления',
        }

    )

    status = drf_filters.ChoiceFilter(
        choices=[
            ('active', 'Активные'),
            ('archived', 'Архивные')
        ],
        label='Статус задач'
    )

    class Meta:
        model = Task
        fields = ['status', 'ordering']

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)

        task_status = self.data.get('status')
        if task_status == 'active':
            queryset = queryset.filter(deadline__gte=timezone.now())  # Предполагаем, что у вас есть поле is_archived
        elif task_status == 'archived':
            queryset = queryset.filter(deadline__lt=timezone.now())

        return queryset


class StudentMyTasksFilter(drf_filters.FilterSet):
    ordering = drf_filters.OrderingFilter(
        fields=(
            ('created_at', 'createdAt'),
        ),

        # labels do not need to retain order
        field_labels={
            'created_at': 'По дате добавления',
        }

    )

    status = drf_filters.ChoiceFilter(
        choices=[
            ('active', 'Активные'),
            ('archived', 'Архивные')
        ],
        label='Статус задач'
    )

    class Meta:
        model = Task
        fields = ['status', 'ordering']

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)

        task_status = self.data.get('status')
        if task_status == 'active':
            queryset = queryset.filter(
                solutions__status=Solution.PENDING)  # Предполагаем, что у вас есть поле is_archived
        elif task_status == 'archived':
            queryset = queryset.filter(Q(solutions__status=Solution.COMPLETED) | Q(solutions__status=Solution.FAILED))

        return queryset
