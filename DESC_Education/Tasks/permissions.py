from rest_framework.permissions import BasePermission
from Users.models import CustomUser


class IsCompanyRole(BasePermission):
    def has_permission(self, request, view):
        if request.method in ('GET', 'HEAD', 'OPTIONS'):
            return True

        return CustomUser.COMPANY_ROLE == request.user.role

    def has_object_permission(self, request, view, obj):
        if request.method in ('GET', 'HEAD', 'OPTIONS'):
            return True

        return CustomUser.COMPANY_ROLE == request.user.role and obj.user == request.user

