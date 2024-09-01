from rest_framework.permissions import BasePermission, SAFE_METHODS
from django.apps import apps

CustomUser = apps.get_model('Users', 'CustomUser')


class IsAuthenticatedAndVerified(BasePermission):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.message = 'Учетные данные не были предоставлены.'

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True

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
        return CustomUser.COMPANY_ROLE == request.user.role



class IsStudentRole(IsAuthenticatedAndVerified):

    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False

        self.message = 'Только для студентов!'
        return CustomUser.STUDENT_ROLE == request.user.role

