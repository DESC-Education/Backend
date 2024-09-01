from rest_framework import serializers
from django.conf import settings
from django.apps import apps
from Tasks.models import (
    TaskCategory,
    FilterCategory,
    Filter,
    Task,
    Solution
)


class FilterSerializer(serializers.ModelSerializer):
    filterCategory = serializers.CharField(source='filter_category')

    class Meta:
        model = Filter
        fields = ('id', 'name', 'filterCategory')


class TaskCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskCategory
        fields = '__all__'


class TaskSerializer(serializers.ModelSerializer):
    filtersId = serializers.PrimaryKeyRelatedField(source="filters", queryset=Filter.objects.all(),
                                                   many=True, required=False, write_only=True)
    categoryId = serializers.PrimaryKeyRelatedField(source="category", queryset=TaskCategory.objects.all(),
                                                    write_only=True)
    category = TaskCategorySerializer(read_only=True)
    filters = FilterSerializer(many=True, read_only=True)
    profile = serializers.SerializerMethodField(read_only=True)
    createdAt = serializers.DateTimeField(source='created_at', read_only=True)

    class Meta:
        model = Task
        fields = ('id', 'user', 'createdAt', 'title', 'description', 'deadline', 'file', 'category',
                  'filters', 'profile', "categoryId", "filtersId")
        read_only_fields = ['id', 'user']

    @staticmethod
    def get_profile(obj):
        try:
            profile = apps.get_model('Profiles', 'CompanyProfile').objects.get(user=obj.user)
            return ProfileTaskSerializer(profile).data
        except:
            return None

    def __init__(self, *args, **kwargs):
        super(TaskSerializer, self).__init__(*args, **kwargs)
        request = self.context.get('request')

        if request and request.method == 'PATCH':
            for field in self.fields:
                self.fields[field].required = False
        if request and request.method == 'GET':
            for field in self.fields:
                self.fields[field].required = False

    def validate(self, attrs):
        request = self.context.get('request')
        if request and request.method == 'PATCH':
            if not attrs:
                raise serializers.ValidationError({"data": "Необходимо передать хотя бы одно поле для изменения."})

        return attrs


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


class SolutionSerializer(serializers.ModelSerializer):
    """
        Создание студент: taskId, description, file

    """

    # write_only
    taskId = serializers.PrimaryKeyRelatedField(
        source="task", queryset=Task.objects.all(), write_only=True)

    # read_only
    createdAt = serializers.DateTimeField(source='created_at', read_only=True)
    companyComment = serializers.CharField(source='company_comment', read_only=True)
    task = TaskSerializer(read_only=True)

    # read and write


    class Meta:
        model = Solution
        fields = ('id', 'task', 'user', 'description', 'file',
                  'companyComment', 'status', 'createdAt', 'taskId')
        read_only_fields = ['id', 'task', 'createdAt', 'companyComment', 'user', 'status']
