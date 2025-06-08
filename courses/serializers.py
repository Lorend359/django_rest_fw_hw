from rest_framework import serializers

from .models import Course, Lesson, Subscription
from .validators import validate_video_url


class LessonShortSerializer(serializers.ModelSerializer):
    """
    Короткий сериализатор для урока.

    Используется внутри курса для отображения краткой информации об уроке.
    """

    class Meta:
        model = Lesson
        fields = ("id", "title", "description", "video_url")
        read_only_fields = ["owner"]


class CourseSerializer(serializers.ModelSerializer):
    """
    Сериализатор для курса.

    Включает количество уроков и список кратких данных об уроках.
    """

    lesson_count = serializers.SerializerMethodField()
    lessons = LessonShortSerializer(many=True, read_only=True)
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = "__all__"
        read_only_fields = ["owner"]

    def get_lesson_count(self, obj):
        """Возвращает количество уроков в курсе."""
        return obj.lessons.count()

    def get_is_subscribed(self, obj):
        """Определяет, подписан ли текущий пользователь на курс."""
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return Subscription.objects.filter(user=request.user, course=obj).exists()
        return False


class LessonSerializer(serializers.ModelSerializer):
    """
    Полный сериализатор для урока.

    Используется для отображения и редактирования всех полей урока.
    """

    video_url = serializers.URLField(required=False, validators=[validate_video_url])

    class Meta:
        model = Lesson
        fields = '__all__'
        read_only_fields = ['owner']

