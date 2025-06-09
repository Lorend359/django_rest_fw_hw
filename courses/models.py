from django.conf import settings
from django.db import models


class Course(models.Model):
    """
    Модель курса.

    Содержит информацию о курсе: название, превью, описание, цена и владельца.
    """

    title = models.CharField(max_length=255)
    preview = models.ImageField(upload_to="course_previews/", blank=True, null=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    price_id = models.CharField(max_length=500, blank=True, null=True)  # ⬅️ вот это добавь
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="courses")

    def __str__(self):
        return self.title



class Lesson(models.Model):
    """
    Модель урока.

    Связана с курсом и содержит название, описание, превью, ссылку на видео и владельца.
    """

    course = models.ForeignKey(Course, related_name="lessons", on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    preview = models.ImageField(upload_to="lesson_previews/", blank=True, null=True)
    video_url = models.URLField(blank=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="lessons")

    def __str__(self):
        """Возвращает строковое представление урока с указанием курса."""
        return f"{self.title} ({self.course.title})"


class Subscription(models.Model):
    """
    Модель подписки пользователя на курс.

    Содержит ссылку на пользователя и курс. Один пользователь не может быть подписан на один курс дважды.
    """

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="subscriptions")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="subscriptions")

    class Meta:
        unique_together = ("user", "course")
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"

    def __str__(self):
        """Возвращает строковое представление подписки."""
        return f"{self.user.email} -> {self.course.title}"
