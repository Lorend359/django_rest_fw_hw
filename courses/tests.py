from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model

from courses.models import Lesson, Course, Subscription

User = get_user_model()


class LessonAPITestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="test@example.com", password="302010Pass")
        self.client.force_authenticate(user=self.user)
        self.course = Course.objects.create(title="Курс", description="Описание", owner=self.user)

    def test_create_lesson(self):
        """Создание урока"""
        data = {
            "title": "Тестовый урок",
            "description": "Описание",
            "course": self.course.id,
            "video_url": "https://youtube.com/watch?v=abc123"
        }
        response = self.client.post(reverse("courses:lesson_create_list"), data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_get_lessons(self):
        """Получение списка уроков"""
        Lesson.objects.create(
            title="Урок 1",
            description="Описание",
            course=self.course,
            video_url="https://youtube.com/watch?v=abc123",
            owner=self.user
        )
        response = self.client.get(reverse("courses:lesson_create_list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data["results"]), 1)  # pagination!

    def test_retrieve_lesson(self):
        """Получение одного урока"""
        lesson = Lesson.objects.create(
            title="Урок 1",
            description="Описание",
            course=self.course,
            video_url="https://youtube.com/watch?v=abc123",
            owner=self.user
        )
        url = reverse("courses:lesson-detail", args=[lesson.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], lesson.id)

    def test_update_lesson(self):
        """Обновление урока"""
        lesson = Lesson.objects.create(
            title="Старое",
            description="Описание",
            course=self.course,
            video_url="https://youtube.com/watch?v=abc123",
            owner=self.user
        )
        url = reverse("courses:lesson-detail", args=[lesson.id])
        response = self.client.patch(url, {"title": "Новое"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Новое")

    def test_delete_lesson(self):
        """Удаление урока"""
        lesson = Lesson.objects.create(
            title="На удаление",
            description="Описание",
            course=self.course,
            video_url="https://youtube.com/watch?v=abc123",
            owner=self.user
        )
        url = reverse("courses:lesson-detail", args=[lesson.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Lesson.objects.filter(id=lesson.id).exists())


class SubscriptionAPITestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="sub@example.com", password="302010Pass")
        self.client.force_authenticate(user=self.user)
        self.course = Course.objects.create(title="Курс", description="Описание", owner=self.user)

    def test_toggle_subscription(self):
        """Добавление и удаление подписки"""
        url = reverse("courses:subscription-toggle")
        data = {"course_id": self.course.id}

        # Добавление
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("добавлена", response.data["message"].lower())
        self.assertTrue(Subscription.objects.filter(user=self.user, course=self.course).exists())

        # Удаление
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("удалена", response.data["message"].lower())
        self.assertFalse(Subscription.objects.filter(user=self.user, course=self.course).exists())
