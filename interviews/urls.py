from django.urls import path

from . import views


app_name = "interviews"


urlpatterns = [
    path(
        "",
        views.interview_home,
        name="interview_home"
    ),

    path(
        "practice/<int:question_id>/",
        views.practice_question,
        name="practice_question"
    ),

    path(
        "progress/",
        views.interview_progress,
        name="interview_progress"
    ),

    path(
        "skills/",
        views.skill_questions,
        name="skill_questions"
    ),

    path(
    "projects/",
    views.project_questions,
    name="project_questions"
),
]