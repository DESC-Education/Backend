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


class TaskSerializer(serializers.ModelSerializer):
    # write_only
    filtersId = serializers.PrimaryKeyRelatedField(source="filters", queryset=Filter.objects.all(),
                                                   many=True, required=False, write_only=True)
    categoryId = serializers.PrimaryKeyRelatedField(source="category", queryset=TaskCategory.objects.all(),
                                                    write_only=True)

    # read_only
    category = TaskCategorySerializer(read_only=True)
    catFilters = serializers.SerializerMethodField()
    profile = serializers.SerializerMethodField(read_only=True)
    createdAt = serializers.DateTimeField(source='created_at', read_only=True)
    solutionsCount = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = ('id', 'user', 'createdAt', 'title', 'description', 'deadline', 'file', 'category',
                  'catFilters', 'profile', "categoryId", "filtersId", 'solutionsCount')
        read_only_fields = ['id', 'user']

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

    # @staticmethod
    # def get_profile(obj) -> dict:
    #     return ProfileTaskSerializer(obj.user.get_profile()).data

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


class SolutionSerializer(serializers.ModelSerializer):
    """
        Создание студент: taskId, description, file

    """

    # write_only
    taskId = serializers.PrimaryKeyRelatedField(
        source="task", queryset=Task.objects.filter(deadline__gte=timezone.now()), write_only=True)

    # read_only
    status = serializers.CharField(read_only=True)
    createdAt = serializers.DateTimeField(source='created_at', read_only=True)
    companyComment = serializers.CharField(source='company_comment', read_only=True)
    task = TaskSerializer(read_only=True)

    # read and write

    class Meta:
        model = Solution
        fields = ('id', 'task', 'user', 'description', 'file',
                  'companyComment', 'status', 'createdAt', 'taskId')
        read_only_fields = ['id', 'task', 'createdAt', 'companyComment', 'user', 'status']
