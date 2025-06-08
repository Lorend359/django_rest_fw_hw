from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import CustomTokenObtainPairView, PaymentListAPIView, UserCreateAPIView, UserRetrieveUpdateAPIView

urlpatterns = [
    path("profile/<int:pk>/", UserRetrieveUpdateAPIView.as_view(), name="user-profile"),
    path("register/", UserCreateAPIView.as_view(), name="user-register"),
    path("payments/", PaymentListAPIView.as_view(), name="payment-list"),
    path("token/", CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("<int:pk>/", UserRetrieveUpdateAPIView.as_view(), name="user-profile"),
]
