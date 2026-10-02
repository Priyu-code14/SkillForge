from django.contrib import admin

from .models import InterviewQuestion, InterviewSession


@admin.register(InterviewQuestion)
class InterviewQuestionAdmin(admin.ModelAdmin):
    list_display = (
        "question",
        "target_role",
        "category",
        "difficulty",
        "created_at",
    )

    list_filter = (
        "target_role",
        "category",
        "difficulty",
    )

    search_fields = (
        "question",
        "explanation",
    )


@admin.register(InterviewSession)
class InterviewSessionAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "question",
        "confidence",
        "practiced_at",
    )

    list_filter = (
        "confidence",
        "practiced_at",
    )

    search_fields = (
        "user__username",
        "question__question",
    )