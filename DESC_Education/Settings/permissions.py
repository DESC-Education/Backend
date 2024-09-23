from rest_framework.permissions import BasePermission, SAFE_METHODS
from django.apps import apps
from django.contrib.auth.models import AnonymousUser

BaseProfile = apps.get_model('Profiles', 'StudentProfile')
CustomUser = apps.get_model('Users', 'CustomUser')
Task = apps.get_model('Tasks', 'Task')


class IsAuthenticatedAndVerified(BasePermission):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.message = 'Учетные данные не были предоставлены.'

    def has_permission(self, request, view):
        # if request.method in SAFE_METHODS:
        #     return True

        user = request.user
        if not bool(user and user.is_authenticated):
            return False

        self.message = 'Необходимо подтвердить адрес электронной почты'
        return user.is_verified

    def has_object_permission(self, request, view, obj):
        self.message = 'К изменению доступны объекты созданые только вами'
        return obj.user == request.user


class IsCompanyRole(IsAuthenticatedAndVerified):
    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False

        self.message = 'Только для компаний!'
        if not CustomUser.COMPANY_ROLE == request.user.role:
            return False

        self.message = 'Необходимо подтвердить профиль!'
        return request.user.get_profile().verification == BaseProfile.VERIFIED

    def has_object_permission(self, request, view, obj):
        self.message = 'К изменению доступны объекты созданые только вами'
        if obj.user == request.user:
            return True
        if isinstance(obj, Task):
            if obj.task.user == request.user:
                return True
        return False




class IsCompanyOrStudentRole(IsAuthenticatedAndVerified):
    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False

        if not super().has_permission(request, view):
            return False

        self.message = 'Только для компаний и студентов!'
        if request.user.role not in [CustomUser.COMPANY_ROLE, CustomUser.STUDENT_ROLE]:
            return False

        self.message = 'Необходимо подтвердить профиль!'
        return request.user.get_profile().verification == BaseProfile.VERIFIED


class IsAdminRole(BasePermission):
    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False

        if type(request.user) == AnonymousUser:
            return False

        self.message = 'Только для модераторов!'
        if request.user.role not in [CustomUser.ADMIN_ROLE, CustomUser.UNIVERSITY_ADMIN_ROLE]:
            return False

        return True


class EvaluateCompanyRole(IsCompanyRole):
    def has_object_permission(self, request, view, obj):
        self.message = 'К изменению доступны объекты созданые только вами'
        return obj.task.user == request.user


class IsStudentRole(IsAuthenticatedAndVerified):

    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False

        if type(request.user) == AnonymousUser:
            return False

        self.message = 'Только для студентов!'
        if not CustomUser.STUDENT_ROLE == request.user.role:
            return False

        self.message = 'Необходимо подтвердить профиль!'
        return request.user.get_profile().verification == BaseProfile.VERIFIED
