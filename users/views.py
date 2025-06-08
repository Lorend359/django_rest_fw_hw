from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, serializers
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import CustomUser, Payment
from .permissions import IsProfileOwner
from .serializers import PaymentSerializer, PrivateUserSerializer, PublicUserSerializer, UserSerializer


class UserRetrieveUpdateAPIView(generics.RetrieveUpdateAPIView):
    """Получение и редактирование профиля пользователя.

    Публичный просмотр — для всех,
    Полный доступ — только для владельца профиля.
    """

    queryset = CustomUser.objects.all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.user == self.get_object():
            return PrivateUserSerializer
        return PublicUserSerializer

    def get_permissions(self):
        if self.request.method in ["PUT", "PATCH"]:
            return [IsAuthenticated(), IsProfileOwner()]
        return [IsAuthenticated()]


class UserCreateAPIView(generics.CreateAPIView):
    """Регистрация нового пользователя."""

    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]


class PaymentListAPIView(generics.ListAPIView):
    """Список всех платежей с фильтрацией и сортировкой.

    Доступно только авторизованным пользователям.
    """

    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ["course", "lesson", "payment_method"]
    ordering_fields = ["payment_date"]
    ordering = ["-payment_date"]  # новые сверху


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Переопределённый сериализатор JWT для включения email и авторизации по нему."""

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["email"] = user.email
        return token

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        user = CustomUser.objects.filter(email=email).first()
        if user and user.check_password(password):
            return super().validate(attrs)

        raise serializers.ValidationError("Invalid credentials")


class CustomTokenObtainPairView(TokenObtainPairView):
    """Представление для получения JWT-токенов по email и паролю."""

    serializer_class = CustomTokenObtainPairSerializer
