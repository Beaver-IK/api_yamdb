from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdminOrReadOnly(BasePermission):
    """Разрешение только администраторам на выполнение операций записи.
    Чтение доступно всем.
    """

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user.is_authenticated and (
            request.user.is_superuser or getattr(
                request.user,
                'role',
                None
            ) == 'admin'
        )


class IsAuthorOrModeratorOrAdmin(BasePermission):
    """
    Разрешение для авторов, модераторов и администраторов.
    - Авторы могут редактировать и удалять свои комментарии.
    - Модераторы и админы могут редактировать и удалять любые комментарии.
    - Чтение доступно всем.
    """

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        if request.user.is_superuser or getattr(
            request.user,
            'role',
            None
        ) in ('admin', 'moderator'):
            return True
        return obj.author == request.user
