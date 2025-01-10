from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdminOrReadOnly(BasePermission):
    """Разрешение только администраторам на выполнение операций записи.
    Чтение доступно всем.
    """

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return (
            request.user.is_authenticated
            and getattr(request.user, 'role', None) == 'admin'
        )
