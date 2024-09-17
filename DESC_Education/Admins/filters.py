from Profiles.models import (
    ProfileVerifyRequest,
)
from django.db.models import Q
from Users.models import (
    CustomUser,
)

from django_filters import rest_framework as filters


class ProfileVerifyRequestFilter(filters.FilterSet):
    status = filters.ChoiceFilter(choices=ProfileVerifyRequest.STATUS_CHOICES)
    role = filters.ChoiceFilter(choices=CustomUser.ROLE_CHOISES[:2])

    class Meta:
        model = ProfileVerifyRequest
        fields = ['status', 'role']

    def filter_queryset(self, queryset):
        # Получаем значение фильтров из запроса
        status = self.request.query_params.get('status')
        role = self.request.query_params.get('role')

        # Фильтрация по статусу
        if status:
            queryset = queryset.filter(status=status)

        # Кастомная логика для фильтрации по роли
        if role:
            profile_filter = Q(student_profile__user__role=role) | Q(company_profile__user__role=role)
            queryset = queryset.filter(profile_filter)

        return queryset
