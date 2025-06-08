from rest_framework.permissions import BasePermission


class IsModerator(BasePermission):
    """Разрешение: пользователь должен быть в группе 'Модераторы'."""

    def has_permission(self, request, view):
        return (
            request.user and request.user.is_authenticated and request.user.groups.filter(name="Модераторы").exists()
        )


class IsOwner(BasePermission):
    """Разрешение: объект должен принадлежать текущему пользователю."""

    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user


class IsProfileOwner(BasePermission):
    """Разрешение: доступ разрешён только владельцу профиля."""

    def has_object_permission(self, request, view, obj):
        return obj == request.user


class IsNotModerator(BasePermission):
    """Разрешение: пользователь НЕ должен быть в группе 'Модераторы'."""

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and not request.user.groups.filter(name="Модераторы").exists()
        )
