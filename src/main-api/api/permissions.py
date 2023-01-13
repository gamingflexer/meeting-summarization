from rest_framework import permissions

class IsOwner(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user

from decouple import config

DEBUG = config('DEBUG', cast=bool)

def user_auth_required():
    if DEBUG:
        permission_classes = (permissions.AllowAny,)
    else:
        permission_classes = (permissions.IsAuthenticated, IsOwner,)
    return permission_classes