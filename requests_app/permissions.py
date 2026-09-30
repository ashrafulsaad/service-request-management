from rest_framework import permissions


class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == "admin"
        )


class ServiceRequestPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        user = request.user

        if user.role == "admin":
            return True

        if request.method in permissions.SAFE_METHODS:
            if user.role == "officer":
                return obj.assigned_officer == user

            return obj.citizen == user

        if user.role == "citizen":
            return (
                obj.citizen == user
                and obj.status == "pending"
            )

        if user.role == "officer":
            return obj.assigned_officer == user

        return False
