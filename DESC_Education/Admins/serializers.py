import random
from django.db.models import Count, Q
from rest_framework import serializers

from Profiles.models import (
    ProfileVerifyRequest,
)


class ProfileVerifyRequestsListSerializer(serializers.ModelSerializer):
    userType = serializers.CharField(source="profile.user.role")
    firstName = serializers.CharField(source="profile.first_name")
    lastName = serializers.CharField(source="profile.last_name")
    email = serializers.CharField(source="profile.user.email")

    class Meta:
        model = ProfileVerifyRequest
        fields = ['id', 'created_at', 'status', 'comment', 'admin', "userType", "firstName", "lastName", "email"]
