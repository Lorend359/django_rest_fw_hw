import stripe
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, serializers
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

from courses.models import Course
from courses.services.stripe_service import (create_stripe_price, create_stripe_product, create_stripe_session,
                                             get_stripe_session_status)

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

    def post(self, request, *args, **kwargs):
        course_id = request.data.get("course_id")
        course = get_object_or_404(Course, id=course_id)

        product_id = create_stripe_product(course.title)
        price_id = create_stripe_price(product_id, course.price)

        success_url = "http://127.0.0.1:8000/success/"
        cancel_url = "http://127.0.0.1:8000/cancel/"

        session_url = create_stripe_session(price_id, success_url, cancel_url)

        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{"price": price_id, "quantity": 1}],
            mode="payment",
            success_url=success_url,
            cancel_url=cancel_url,
        )

        Payment.objects.create(
            user=request.user,
            course=course,
            amount=course.price,
            payment_method="card",
            stripe_payment_url=session.url,
            stripe_session_id=session.id,  # <-- Добавь это
        )

        return Response({"payment_url": session_url})


class StripePaymentStatusAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        session_id = request.data.get("session_id")

        if not session_id:
            return Response({"error": "session_id is required"}, status=400)

        try:
            status = get_stripe_session_status(session_id)
            return Response({"status": status})
        except stripe.error.StripeError as e:
            return Response({"error": str(e)}, status=400)
