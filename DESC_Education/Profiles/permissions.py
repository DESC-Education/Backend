from rest_framework.permissions import BasePermission, SAFE_METHODS
from Users.models import CustomUser


class IsCompanyOrStudentRole(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True

        if not bool(request.user and request.user.is_authenticated):
            return False

        return request.user.role in (CustomUser.COMPANY_ROLE, CustomUser.STUDENT_ROLE)

    def has_object_permission(self, request, view, obj):
        return obj.user == request.user

