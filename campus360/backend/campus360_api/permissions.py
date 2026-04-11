"""
Custom permissions for role-based access control.
"""
from rest_framework.permissions import BasePermission


class IsStudent(BasePermission):
    """Allow access only to users with student role."""
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return hasattr(request.user, 'profile') and request.user.profile.role == 'student'


class IsFaculty(BasePermission):
    """Allow access only to users with faculty role."""
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return hasattr(request.user, 'profile') and request.user.profile.role == 'faculty'


class IsAdmin(BasePermission):
    """Allow access only to users with admin role."""
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return hasattr(request.user, 'profile') and request.user.profile.role == 'admin'


class IsFacultyOrAdmin(BasePermission):
    """Allow access to faculty or admin users."""
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if not hasattr(request.user, 'profile'):
            return False
        return request.user.profile.role in ('faculty', 'admin')


class IsOwnerOrAdmin(BasePermission):
    """Allow access to the object owner or admin."""
    def has_object_permission(self, request, view, obj):
        if request.user.profile.role == 'admin':
            return True
        if hasattr(obj, 'profile_id'):
            return obj.profile_id == request.user.profile.id
        if hasattr(obj, 'user_id'):
            return obj.user_id == request.user.id
        return False
