from rest_framework.exceptions import ValidationError


def validate_video_url(value):
    """
    Проверяет, что ссылка на видео указывает на youtube.com
    """
    if "youtube.com" not in value and "youtu.be" not in value:
        raise ValidationError("Only YouTube links are allowed.")
