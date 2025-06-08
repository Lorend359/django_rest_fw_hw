from django.shortcuts import get_object_or_404
from rest_framework import generics, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from users.permissions import IsNotModerator, IsOwner

from .models import Course, Lesson, Subscription
from .paginators import StandardPagination
from .serializers import CourseSerializer, LessonSerializer


class CourseViewSet(viewsets.ModelViewSet):
    """Вьюсет для работы с курсами (CRUD)."""

    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    pagination_class = StandardPagination

    def get_permissions(self):
        """Настройка прав доступа для разных действий с курсами."""
        if self.action in ["list", "retrieve"]:
            self.permission_classes = [IsAuthenticated]
        elif self.action in ["update", "partial_update"]:
            self.permission_classes = [IsAuthenticated, IsNotModerator | IsOwner]
        elif self.action == "create":
            self.permission_classes = [IsAuthenticated, IsNotModerator]
        elif self.action == "destroy":
            self.permission_classes = [IsAuthenticated, IsOwner]
        return [permission() for permission in self.permission_classes]

    def perform_create(self, serializer):
        """Присваивает текущего пользователя как владельца курса."""
        serializer.save(owner=self.request.user)

    def destroy(self, request, *args, **kwargs):
        """Проверяет права перед удалением курса."""
        instance = self.get_object()
        self.check_object_permissions(request, instance)
        return super().destroy(request, *args, **kwargs)


class LessonListCreateAPIView(generics.ListCreateAPIView):
    """Просмотр и создание уроков."""

    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    pagination_class = StandardPagination

    def get_permissions(self):
        """Настройка прав доступа для GET и POST запросов."""
        if self.request.method == "GET":
            self.permission_classes = [IsAuthenticated]
        elif self.request.method == "POST":
            self.permission_classes = [IsAuthenticated, IsNotModerator]
        return [permission() for permission in self.permission_classes]

    def perform_create(self, serializer):
        """Присваивает текущего пользователя как владельца урока."""
        serializer.save(owner=self.request.user)


class LessonRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    """Просмотр, редактирование и удаление конкретного урока."""

    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer

    def get_permissions(self):
        """Настройка прав доступа для PATCH/PUT/DELETE запросов."""
        if self.request.method in ["PUT", "PATCH"]:
            self.permission_classes = [IsAuthenticated, IsNotModerator | IsOwner]
        elif self.request.method == "DELETE":
            self.permission_classes = [IsAuthenticated, IsOwner]
        else:
            self.permission_classes = [IsAuthenticated]
        return [permission() for permission in self.permission_classes]


class SubscriptionToggleAPIView(APIView):
    """APIView для подписки или отписки от курса."""

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        """Добавляет или удаляет подписку на курс."""
        user = request.user
        course_id = request.data.get("course_id")
        course = get_object_or_404(Course, id=course_id)

        subscription = Subscription.objects.filter(user=user, course=course)

        if subscription.exists():
            subscription.delete()
            return Response({"message": "Подписка удалена"})
        else:
            Subscription.objects.create(user=user, course=course)
            return Response({"message": "Подписка добавлена"})
