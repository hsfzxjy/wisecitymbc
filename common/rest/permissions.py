#encoding=utf8
from rest_framework import permissions
from django.contrib import messages
from copy import deepcopy
from rest_framework.permissions import *

def own_object_permission(field_name):

    class P(permissions.BasePermission):

        def has_object_permission(self, request, view, obj):
            print hasattr(obj, field_name) and getattr(obj, field_name) == request.user
            if hasattr(obj, field_name) and getattr(obj, field_name) == request.user:
                return True 
            else:
                return False

    return P

def own_object_or_superuser_permission(field_name):

    class P(permissions.BasePermission):

        def has_object_permission(self, request, view, obj):
            if request.user.is_superuser or hasattr(obj, field_name) and getattr(obj, field_name) == request.user:
                return True 
            else:
                return False

    return P

def custom_perms_map(perms_map):

    perms = deepcopy(DjangoModelPermissionsOrAnonReadOnly.perms_map)
    perms.update(perms_map)

    class P(DjangoModelPermissionsOrAnonReadOnly):

        perms_map = perms

    return P

def custom_perm(perm):

    class P(BasePermission):

        def has_permission(self, request, view):
            result = request.user.is_authenticated() and request.user.has_perm(perm)
            if not result:
                messages.warning(request._request, u'啊哦，亲～这里不允许访问啵～你要有更厉害的权限才行哟')

            return result

    return P