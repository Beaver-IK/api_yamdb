from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdminOrReadOnly(BasePermission):
    """Разрешение только администраторам на выполнение операций записи.
    Чтение доступно всем.
    """

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user.is_authenticated and (
            request.user.is_superuser or getattr(request.user, 'role', None) == 'admin'
        )


class IsAdminOrAuthor(BasePermission):
    """Разрешение только для администраторов или авторов."""

    def has_object_permission(self, request, view, obj):
        return request.user.is_authenticated and (
            request.user.is_superuser or request.user.is_staff or obj.author == request.user
        )


class IsAuthorOrReadOnly(BasePermission):
    """
    Пользователь может редактировать/удалять только свои комментарии.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return request.user.is_authenticated and obj.author == request.user


class IsStaffOrAuthor(BasePermission):
    """
    Разрешение для модераторов или авторов.
    Модератор и администратор могут редактировать чужие комментарии, автор — только свои.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        if not request.user.is_authenticated:
            return False
        if request.user.is_superuser or request.user.role == 'moderator':
            return True
        return obj.author == request.user
