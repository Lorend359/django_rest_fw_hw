from django.contrib import admin
from .models import Course, Lesson, Subscription

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("title", "price", "owner")
    search_fields = ("title", "owner__email")

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ("title", "course", "owner")
    search_fields = ("title", "course__title")

@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ("user", "course")
    search_fields = ("user__email", "course__title")
