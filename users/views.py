from rest_framework import generics, serializers
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.filters import OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import CustomUser, Payment
from .serializers import UserSerializer, PaymentSerializer


class UserRetrieveUpdateAPIView(generics.RetrieveUpdateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]


class UserCreateAPIView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]


class PaymentListAPIView(generics.ListAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['course', 'lesson', 'payment_method']
    ordering_fields = ['payment_date']
    ordering = ['-payment_date']  # новые сверху


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['email'] = user.email
        return token

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        user = CustomUser.objects.filter(email=email).first()
        if user and user.check_password(password):
            return super().validate(attrs)

        raise serializers.ValidationError("Invalid credentials")


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
