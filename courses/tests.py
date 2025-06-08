from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model

from courses.models import Lesson, Course

User = get_user_model()

class LessonAPITestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="test@example.com", password="302010Pass")
        self.client.force_authenticate(user=self.user)

        self.course = Course.objects.create(
            title="Тестовый курс",
            description="Описание",
            owner=self.user
        )

        self.lesson_data = {
            "title": "Тестовый урок",
            "description": "Описание урока",
            "course": self.course.id,
            "video_url": "https://youtube.com/watch?v=abc123"
        }

    def test_create_lesson(self):
        """Тест создания урока"""
        response = self.client.post(
            reverse("courses:lesson_create_list"),
            self.lesson_data,
            format='json'  # Указание формата запроса
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_get_lessons(self):
        """Тест получения списка уроков"""
        Lesson.objects.create(
            title="Урок 1",
            description="Описание 1",
            course=self.course,
            video_url="https://youtube.com/watch?v=abc123",
            owner=self.user
        )
        response = self.client.get(reverse("courses:lesson_create_list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)


class SubscriptionAPITestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="test2@example.com", password="302010Pass")
        self.client.force_authenticate(user=self.user)

        self.course = Course.objects.create(
            title="Подписка курс",
            description="Описание",
            owner=self.user
        )

    def test_toggle_subscription(self):
        """Тест на добавление и удаление подписки"""
        url = reverse("courses:subscription-toggle")

        # Добавление подписки
        response = self.client.post(url, {"course_id": self.course.id}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("добавлена", response.data["message"].lower())

        # Повторный запрос — удаление
        response = self.client.post(url, {"course_id": self.course.id}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("удалена", response.data["message"].lower())
