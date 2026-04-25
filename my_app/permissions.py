from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsOwnerOrReadOnly(BasePermission):

    def has_object_permission(self, request, view, obj) -> bool:
        # if request.method == 'GET':
        if request.method in SAFE_METHODS:
            return True

        return request.user == obj.publisher


class IsStaffAndAdmin(BasePermission):
    def has_permission(self, request, view) -> bool:
        if view.action == 'get_statistic':

            # app_label.permission_name -> "my_app.can_get_statistic"
            return bool(request.user and request.user.has_perm("my_app.can_get_statistic"))
        return bool(request.user and request.user.is_staff)


class IsAdmin(BasePermission):
    message = 'А ВОТ НИЗЯ ТЕБЕ'

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_superuser)


class IsAdminOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.is_superuser
        )


class CreateActionPermanentBlocked(BasePermission):
    def has_permission(self, request, view):
        if view.action == 'create':
            return False
        return True
