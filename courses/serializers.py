from rest_framework import serializers

from .models import Course, Lesson


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

    class Meta:
        model = Course
        fields = "__all__"
        read_only_fields = ["owner"]

    def get_lesson_count(self, obj):
        """
        Возвращает количество уроков в курсе.
        """
        return obj.lessons.count()


class LessonSerializer(serializers.ModelSerializer):
    """
    Полный сериализатор для урока.

    Используется для отображения и редактирования всех полей урока.
    """

    class Meta:
        model = Lesson
        fields = "__all__"
