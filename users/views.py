import stripe
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, serializers
from rest_framework.exceptions import NotFound
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

from courses.models import Course
from courses.services.stripe_services import (
    create_stripe_price,
    create_stripe_product,
    create_stripe_session,
    get_stripe_session_status,
)

from .models import CustomUser, Payment
from .permissions import IsProfileOwner
from .serializers import PaymentSerializer, PrivateUserSerializer, PublicUserSerializer, UserSerializer


class UserRetrieveUpdateAPIView(generics.RetrieveUpdateAPIView):
    """Получение и редактирование профиля пользователя."""

    queryset = CustomUser.objects.all()

    def get_serializer_class(self):
        if self.request.user == self.get_object():
            return PrivateUserSerializer
        return PublicUserSerializer

    def get_permissions(self):
        if self.request.method in ["PUT", "PATCH"]:
            self.permission_classes = [IsAuthenticated, IsProfileOwner]
        else:
            self.permission_classes = [IsAuthenticated]
        return [permission() for permission in self.permission_classes]


class UserCreateAPIView(generics.CreateAPIView):
    """Регистрация нового пользователя."""

    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]


class PaymentListAPIView(generics.ListAPIView):
    """Список всех платежей с фильтрацией и сортировкой."""

    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ["course", "lesson", "payment_method"]
    ordering_fields = ["payment_date"]
    ordering = ["-payment_date"]


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


class CreatePaymentAPIView(APIView):
    """Создание Stripe-сессии и сохранение платежа."""

    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["course_id"],
            properties={
                "course_id": openapi.Schema(type=openapi.TYPE_INTEGER, description="ID курса"),
            },
        ),
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "payment_url": openapi.Schema(type=openapi.TYPE_STRING, description="Ссылка на оплату"),
                },
            )
        },
    )
    def post(self, request, *args, **kwargs):
        course_id = request.data.get("course_id")
        course = get_object_or_404(Course, id=course_id)

        product_id = create_stripe_product(course.title)
        price_id = create_stripe_price(product_id, course.price)

        success_url = "http://127.0.0.1:8000/success/"
        cancel_url = "http://127.0.0.1:8000/cancel/"

        session = create_stripe_session(price_id, success_url, cancel_url)

        Payment.objects.create(
            user=request.user,
            course=course,
            amount=course.price,
            payment_method="card",
            stripe_payment_url=session,
            stripe_session_id=session.split("/")[-1],  # или session.id, если возвращаешь объект
        )

        return Response({"payment_url": session})


class StripePaymentStatusAPIView(APIView):
    """Получение статуса Stripe-сессии по её ID."""

    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["session_id"],
            properties={
                "session_id": openapi.Schema(type=openapi.TYPE_STRING, description="ID сессии Stripe"),
            },
        ),
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "status": openapi.Schema(type=openapi.TYPE_STRING, description="Статус оплаты"),
                },
            )
        },
    )
    def post(self, request, *args, **kwargs):
        session_id = request.data.get("session_id")

        if not session_id:
            raise NotFound("session_id is required")

        try:
            status = get_stripe_session_status(session_id)
            return Response({"status": status})
        except stripe.error.StripeError as e:
            return Response({"error": str(e)}, status=400)
