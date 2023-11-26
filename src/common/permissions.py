from rest_framework.permissions import BasePermission
from django.conf import settings


class IsSuperUser(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_superuser == True