from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsAdminOrReadOnly(BasePermission):
    """Разрешает запись только администраторам; чтение доступно всем."""

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user.is_authenticated and request.user.is_admin


class IsAuthorOrModeratorOrAdmin(BasePermission):
    """
    Разрешение для авторов, модераторов и администраторов:
    - Автор может редактировать/удалять только свои комментарии,
    - Модератор/админ — любые,
    - Чтение доступно всем.
    """

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        if request.user.is_admin or request.user.is_moderator:
            return True
        return obj.author == request.user


class IsAdminOnly(BasePermission):
    """Разрешение, доступное только администратору."""

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_admin
