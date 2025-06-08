from django.core.management.base import BaseCommand
from django.utils.timezone import now

from courses.models import Course, Lesson
from users.models import CustomUser, Payment


class Command(BaseCommand):
    """Загружает тестовые платежи для первого пользователя."""

    help = "Загрузка тестовых платежей"

    def handle(self, *args, **kwargs):
        user = CustomUser.objects.first()
        course = Course.objects.first()
        lesson = Lesson.objects.first()

        if not user or not (course or lesson):
            self.stdout.write(self.style.ERROR("Нет данных: пользователь, курс или урок отсутствует."))
            return

        Payment.objects.create(user=user, course=course, amount=1500.00, payment_method="cash", payment_date=now())

        Payment.objects.create(user=user, lesson=lesson, amount=700.00, payment_method="transfer", payment_date=now())

        self.stdout.write(self.style.SUCCESS("Платежи успешно добавлены"))
