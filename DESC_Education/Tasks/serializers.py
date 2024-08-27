from rest_framework import serializers
from django.conf import settings
from django.apps import apps
from Tasks.models import (
    Filter,
    Category,
    Task
)


class FilterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Filter
        fields = '__all__'


class TaskDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = '__all__'
        read_only_fields = ['id', 'user', 'deadline']

    def __init__(self, *args, **kwargs):
        super(TaskDetailSerializer, self).__init__(*args, **kwargs)
        request = self.context.get('request')

        if request and request.method == 'PATCH':
            for field in self.fields:
                self.fields[field].required = False

    def validate(self, attrs):
        request = self.context.get('request')
        if request and request.method == 'PATCH':
            if not attrs:
                raise serializers.ValidationError({"data": "Необходимо передать хотя бы одно поле для изменения."})

        return attrs


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = '__all__'
        read_only_fields = ['id', 'user']


class ProfileTaskSerializer(serializers.ModelSerializer):
    companyName = serializers.CharField(source='company_name', read_only=True)
    logoImg = serializers.ImageField(source='logo_img', read_only=True)

    class Meta:
        model = apps.get_model('Profiles', 'CompanyProfile')
        fields = ('companyName', 'logoImg')


class TaskListSerializer(serializers.ModelSerializer):
    profile = serializers.SerializerMethodField()
    createdAt = serializers.DateTimeField(source='created_at')

    class Meta:
        model = Task
        fields = ('title', 'description', 'deadline', 'createdAt', 'profile')

    @staticmethod
    def get_profile(obj):
        try:
            profile = apps.get_model('Profiles', 'CompanyProfile').objects.get(user=obj.user)
            return ProfileTaskSerializer(profile).data
        except:
            return None


class CategorySerializer(serializers.ModelSerializer):
    filters = FilterSerializer(many=True, read_only=True)

    class Meta:
        model = Category
        fields = '__all__'
