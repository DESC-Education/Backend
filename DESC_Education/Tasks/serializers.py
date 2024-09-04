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
    profile = ProfileTaskSerializer(read_only=True)
    createdAt = serializers.DateTimeField(source='created_at', read_only=True)
    solutionsCount = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = ('id', 'user', 'createdAt', 'title', 'description', 'deadline', 'file', 'category',
                  'catFilters', 'profile', "categoryId", "filtersId", 'solutionsCount')
        read_only_fields = ['id', 'user']

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


class StudentTasksMySerializer(serializers.Serializer):
    active_tasks = TaskSerializer(many=True)
    archived_tasks = TaskSerializer(many=True)

    def to_representation(self, instance):
        active_tasks = []
        archived_tasks = []

        for solution in instance:
            if solution.status != solution.PENDING or solution.task.deadline < timezone.now():
                archived_tasks.append(TaskSerializer(solution.task).data)
            else:
                active_tasks.append(TaskSerializer(solution.task).data)

        return {
            'active_tasks': active_tasks,
            'archived_tasks': archived_tasks
        }


class CompanyTasksMySerializer(serializers.Serializer):
    active_tasks = TaskSerializer(many=True)
    archived_tasks = TaskSerializer(many=True)

    def to_representation(self, instance):
        active_tasks = []
        archived_tasks = []

        for task in instance:
            if task.deadline > timezone.now():
                active_tasks.append(TaskSerializer(task).data)
            else:
                archived_tasks.append(TaskSerializer(task).data)

        return {
            'active_tasks': active_tasks,
            'archived_tasks': archived_tasks
        }

    class Meta:
        fields = ('active_tasks', 'archived_tasks')


class TaskListSerializer(serializers.ModelSerializer):
    profile = ProfileTaskSerializer()
    createdAt = serializers.DateTimeField(source='created_at')

    class Meta:
        model = Task
        fields = ('title', 'description', 'deadline', 'createdAt', 'profile', 'category')

    # @staticmethod
    # def get_profile(obj) -> {'logoIMG': "str", 'companyName': "str"}:
    #     try:
    #         profile = apps.get_model('Profiles', 'CompanyProfile').objects.get(user=obj.user)
    #         return ProfileTaskSerializer(profile).data
    #     except:
    #         return None


class SolutionSerializer(serializers.ModelSerializer):
    """
        Создание студент: taskId, description, file

    """

    # write_only
    taskId = serializers.PrimaryKeyRelatedField(
        source="task", queryset=Task.objects.filter(deadline__gte=timezone.now()), write_only=True)

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
