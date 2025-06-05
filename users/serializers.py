from rest_framework import serializers

from .models import CustomUser, Payment


class PublicUserSerializer(serializers.ModelSerializer):
    """Сериализатор для публичного отображения пользователя (без платежей и приватных данных)."""

    class Meta:
        model = CustomUser
        fields = ("id", "email", "phone", "city", "avatar")


class PrivateUserSerializer(serializers.ModelSerializer):
    """Сериализатор для владельца профиля, включает связанные платежи."""

    payments = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = CustomUser
        fields = ("id", "email", "phone", "city", "avatar", "payments")


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для создания/регистрации пользователя."""

    class Meta:
        model = CustomUser
        fields = ("id", "email", "password", "phone", "city", "avatar")
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        """Создание пользователя с хешированием пароля."""
        return CustomUser.objects.create_user(**validated_data)


class PaymentSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Payment (платежей)."""

    class Meta:
        model = Payment
        fields = "__all__"
