from Profiles.models import (
    ProfileVerifyRequest,
)

from django_filters import rest_framework as filters


class ProfileVerifyRequestFilter(filters.FilterSet):
    status = filters.ChoiceFilter(choices=ProfileVerifyRequest.STATUS_CHOICES)

    class Meta:
        model = ProfileVerifyRequest
        fields = ['status']
