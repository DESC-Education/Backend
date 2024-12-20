from django.contrib import admin
from Tasks.models import Task, TaskPattern, TaskCategory, FilterCategory, Filter, Solution, Review



admin.site.register(Task)
admin.site.register(TaskPattern)
admin.site.register(FilterCategory)
admin.site.register(Filter)
admin.site.register(Solution)
admin.site.register(Review)
# Register your models here.
