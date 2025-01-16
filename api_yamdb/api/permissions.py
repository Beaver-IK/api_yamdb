from rest_framework.permissions import BasePermission, SAFE_METHODS


def user_is_admin(user):
    """True, если пользователь — суперпользователь или администратор."""
    return user.is_superuser or getattr(user, 'role', None) == 'admin'


def user_is_moderator(user):
    """Возвращает True, если пользователь — модератор."""
    return getattr(user, 'role', None) == 'moderator'


class IsAdminOrReadOnly(BasePermission):
    """Разрешает запись только администраторам; чтение доступно всем."""

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user.is_authenticated and user_is_admin(request.user)


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
        if user_is_admin(request.user) or user_is_moderator(request.user):
            return True
        return obj.author == request.user


class IsAdminOnly(BasePermission):
    """Разрешение, доступное только администратору."""

    def has_permission(self, request, view):
        return user_is_admin(request.user)
