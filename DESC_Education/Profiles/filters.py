from Profiles.models import (
    Faculty,
)

from django_filters import  rest_framework as filters



class FacultiesFilter(filters.FilterSet):
    universityId = filters.UUIDFilter(field_name='university_id')

    class Meta:
        model = Faculty
        fields = ['universityId']




