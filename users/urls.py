from django.urls import path
from .views import UserRetrieveUpdateAPIView, UserCreateAPIView

urlpatterns = [
    path("profile/<int:pk>/", UserRetrieveUpdateAPIView.as_view(), name="user-profile"),
    path("register/", UserCreateAPIView.as_view(), name="user-register"),
]


