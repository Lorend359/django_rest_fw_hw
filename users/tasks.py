from celery import shared_task
from django.core.mail import send_mail
from courses.models import Course

@shared_task
def send_course_update_email(course_id):
    course = Course.objects.get(id=course_id)
    subscribers = course.subscriptions.select_related('user')

    for sub in subscribers:
        user_email = sub.user.email
        send_mail(
            subject=f"Обновление курса: {course.title}",
            message=f"Материалы курса «{course.title}» были обновлены. Загляните на сайт!",
            from_email="no-reply@example.com",
            recipient_list=[user_email],
            fail_silently=True,
        )
