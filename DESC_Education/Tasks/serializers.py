from rest_framework import serializers
from Tasks.models import (
    Filter,
    Category,
    Task
)


class FilterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Filter
        fields = '__all__'


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = '__all__'
        read_only_fields = ['id', 'user']


    def update(self, instance, validated_data):
        for field in ['title', 'description', 'deadline']:
            if field in validated_data:
                setattr(instance, field, validated_data[field])
        instance.save()
        return instance



class CategorySerializer(serializers.ModelSerializer):
    filters = FilterSerializer(many=True, read_only=True)

    class Meta:
        model = Category
        fields = '__all__'


