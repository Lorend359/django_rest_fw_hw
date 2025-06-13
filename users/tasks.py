from celery import shared_task
from datetime import timedelta
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings


@shared_task
def send_course_update_email(course_id):
    """Фоновая задача: отправка уведомлений подписчикам об обновлении курса, если курс не обновлялся последние 4 часа."""

    from courses.models import Course, Subscription

    course = Course.objects.get(id=course_id)

    # Проверка: обновлялся ли курс в течение последних 4 часов
    if timezone.now() - course.updated_at < timedelta(hours=4):
        print(f"[!] Курс '{course.title}' обновлялся менее 4 часов назад. Уведомление не отправляется.")
        return

    subscriptions = Subscription.objects.select_related("user").filter(course=course)

    for sub in subscriptions:
        send_mail(
            subject=f"Обновление курса: {course.title}",
            message=f"В курсе «{course.title}» появились новые материалы! Загляните на платформу.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[sub.user.email],
            fail_silently=True,
        )
