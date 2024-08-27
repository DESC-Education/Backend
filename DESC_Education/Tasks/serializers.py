from rest_framework import serializers
from django.conf import settings
from django.apps import apps
from Tasks.models import (
    TaskCategory,
    FilterCategory,
    Filter,
    Task,

)


class FilterSerializer(serializers.ModelSerializer):
    filterCategory = serializers.CharField(source='filter_category')

    class Meta:
        model = Filter
        fields = ('id', 'name', 'filterCategory')


class TaskDetailSerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(queryset=TaskCategory.objects.all(), )

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


class TaskCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskCategory
        fields = '__all__'


class TaskCreateSerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(queryset=TaskCategory.objects.all(), )
    filters = serializers.PrimaryKeyRelatedField(queryset=Filter.objects.all(), many=True)

    class Meta:
        model = Task
        fields = '__all__'
        read_only_fields = ['id', 'user']


class TaskSerializer(serializers.ModelSerializer):
    category = TaskCategorySerializer(read_only=True)
    filters = FilterSerializer(many=True, read_only=True)

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
        fields = ('title', 'description', 'deadline', 'createdAt', 'profile', 'category')

    @staticmethod
    def get_profile(obj):
        try:
            profile = apps.get_model('Profiles', 'CompanyProfile').objects.get(user=obj.user)
            return ProfileTaskSerializer(profile).data
        except:
            return None
