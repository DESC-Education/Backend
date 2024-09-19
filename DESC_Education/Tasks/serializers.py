from rest_framework import serializers
from django.conf import settings
from django.apps import apps
from django.utils import timezone
from Tasks.models import (
    TaskCategory,
    FilterCategory,
    Filter,
    Task,
    Solution,
    TaskPattern
)
from Users.models import CustomUser
from Profiles.models import StudentProfile
from Files.serializers import FileSerializer
from Files.models import File


class UserProfileSerializer(serializers.ModelSerializer):
    firstName = serializers.CharField(source='first_name')
    lastName = serializers.CharField(source='last_name')
    logoImg = serializers.ImageField(source='logo_img')

    class Meta:
        model = StudentProfile
        fields = ('firstName', 'lastName', 'logoImg')


class SolutionSerializer(serializers.ModelSerializer):
    """
        Создание студент: taskId, description, file

    """

    # write_only
    files_list = serializers.ListField(
        child=serializers.FileField(),
        write_only=True
    )
    taskId = serializers.PrimaryKeyRelatedField(
        source="task", queryset=Task.objects.filter(deadline__gte=timezone.now()), write_only=True)

    # read_only
    files = FileSerializer(many=True, read_only=True)
    userProfile = serializers.SerializerMethodField(read_only=True)
    status = serializers.ChoiceField(choices=Solution.STATUSES, read_only=True)
    createdAt = serializers.DateTimeField(source='created_at', read_only=True)
    companyComment = serializers.CharField(source='company_comment', read_only=True)

    # read and write

    class Meta:
        model = Solution
        fields = ('id', 'user', 'description', 'files', 'files_list', 'userProfile',
                  'companyComment', 'status', 'createdAt', 'taskId')
        read_only_fields = ['id', 'task', 'createdAt', 'companyComment', 'user', 'status']

    @staticmethod
    def get_userProfile(obj) -> UserProfileSerializer:
        return UserProfileSerializer(obj.user.get_profile()).data

    def create(self, validated_data):
        validated_data.pop('files_list')
        files = self.context.get('view').request.data.getlist('files_list')

        instance = super().create(validated_data)

        for file in files[:6]:
            serializer = FileSerializer(data={"file": file})
            if not serializer.is_valid():
                raise serializers.ValidationError(str(serializer.errors))
            serializer.save(type=File.SOLUTION_FILE, content_object=instance)

        return instance



class ProfileTaskSerializer(serializers.ModelSerializer):
    companyName = serializers.CharField(source='company_name', read_only=True)
    logoImg = serializers.ImageField(source='logo_img', read_only=True)

    class Meta:
        model = apps.get_model('Profiles', 'CompanyProfile')
        fields = ('companyName', 'logoImg')


class FilterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Filter
        fields = ('id', 'name')


class FilterCategorySerializer(serializers.ModelSerializer):
    filters = FilterSerializer(many=True, read_only=True)

    class Meta:
        model = FilterCategory
        fields = ('id', 'name', 'filters')


class TaskCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskCategory
        fields = ('id', 'name')


class TaskCategoryWithFiltersSerializer(serializers.ModelSerializer):
    filterCategories = FilterCategorySerializer(source='filter_categories', many=True)

    class Meta:
        model = TaskCategory
        fields = ('id', 'name', 'filterCategories')


class TaskPatternSerializer(serializers.ModelSerializer):
    catFilters = serializers.SerializerMethodField()

    class Meta:
        model = TaskPattern
        fields = ("id", 'title', 'description', 'catFilters')

    @staticmethod
    def get_catFilters(obj) -> FilterCategorySerializer:
        category_filters = {}
        filters = obj.filters.all()

        for filter in filters:
            cat = filter.filter_category
            cat_name = cat.name

            if cat_name not in category_filters:
                category_filters[cat_name] = {
                    'name': cat_name,
                    'id': cat.id,
                    'filters': []
                }

            category_filters[cat_name]['filters'].append({
                'id': filter.id,
                'name': filter.name,
            })

        return category_filters


class TaskSerializer(serializers.ModelSerializer):
    # write_only
    filtersId = serializers.PrimaryKeyRelatedField(source="filters", queryset=Filter.objects.all(),
                                                   many=True, required=False, write_only=True)
    categoryId = serializers.PrimaryKeyRelatedField(source="category", queryset=TaskCategory.objects.all(),
                                                    write_only=True)
    files_list = serializers.ListField(
        child=serializers.FileField(),
        write_only=True
    )
    # read_only
    files = FileSerializer(many=True, read_only=True)
    category = TaskCategorySerializer(read_only=True)
    catFilters = serializers.SerializerMethodField(read_only=True)
    profile = serializers.SerializerMethodField(read_only=True)
    createdAt = serializers.DateTimeField(source='created_at', read_only=True)
    solutionsCount = serializers.SerializerMethodField(read_only=True)
    solutions = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Task
        fields = ('id', 'user', 'createdAt', 'title', 'description', 'deadline', 'files', 'files_list', 'category',
                  'catFilters', 'profile', "categoryId", "filtersId", 'solutionsCount', 'solutions')
        read_only_fields = ['id', 'user']
        extra_fields = {
            'files': {
                'type': 'list',
                'description': 'Файлы'
            }
        }

    def get_solutions(self, obj) -> ProfileTaskSerializer:
        request = self.context.get('request', None)
        solutions = None
        if request:
            user: CustomUser = request.user
            if user.role == CustomUser.STUDENT_ROLE:
                solutions = obj.solutions.filter(user=user)

        solutions = SolutionSerializer(solutions, many=True).data
        return solutions

    @staticmethod
    def get_profile(obj) -> ProfileTaskSerializer:
        try:
            profile = obj.user.get_profile()
            return ProfileTaskSerializer(profile).data
        except:
            return None

    def get_catFilters(self, obj) -> FilterCategorySerializer:
        category_filters = {}
        filters = obj.filters.all()

        for filter in filters:
            cat = filter.filter_category
            cat_name = cat.name

            if cat_name not in category_filters:
                category_filters[cat_name] = {
                    'name': cat_name,
                    'id': cat.id,
                    'filters': []
                }

            category_filters[cat_name]['filters'].append({
                'id': filter.id,
                'name': filter.name,
            })

        return category_filters

    def get_solutionsCount(self, obj) -> int:
        return obj.solutions.count()


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

    def create(self, validated_data):
        validated_data.pop('files_list')
        files = self.context.get('view').request.data.getlist('files_list')

        instance = super().create(validated_data)

        for file in files[:6]:
            serializer = FileSerializer(data={"file": file})
            if not serializer.is_valid():
                raise serializers.ValidationError(str(serializer.errors))
            serializer.save(type=File.TASK_FILE, content_object=instance)

        return instance



class TaskListSerializer(serializers.ModelSerializer):
    profile = serializers.SerializerMethodField()
    createdAt = serializers.DateTimeField(source='created_at')

    class Meta:
        model = Task
        fields = ('id', 'title', 'description', 'deadline', 'createdAt', 'profile', 'category')

    @staticmethod
    def get_profile(obj) -> ProfileTaskSerializer:
        try:
            profile = obj.user.get_profile()
            return ProfileTaskSerializer(profile).data
        except:
            return None


class EvaluateSolutionSerializer(serializers.ModelSerializer):
    companyComment = serializers.CharField(source='company_comment', write_only=True)

    class Meta:
        model = Solution
        fields = ('status', 'companyComment')
