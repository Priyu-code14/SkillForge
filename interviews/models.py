from django.contrib.auth.models import User
from django.db import models


class InterviewQuestion(models.Model):

    CATEGORY_CHOICES = [
        ("Python", "Python"),
        ("Django", "Django"),
        ("JavaScript", "JavaScript"),
        ("HTML/CSS", "HTML/CSS"),
        ("SQL", "SQL"),
        ("REST API", "REST API"),
        ("Git", "Git"),
        ("HR", "HR"),
        ("Other", "Other"),
    ]

    DIFFICULTY_CHOICES = [
        ("Easy", "Easy"),
        ("Medium", "Medium"),
        ("Hard", "Hard"),
    ]

    # Role-specific question
    target_role = models.ForeignKey(
        "accounts.TargetRole",
        on_delete=models.CASCADE,
        related_name="interview_questions",
        null=True,
        blank=True,
    )

    # Project-specific question
    project = models.ForeignKey(
        "projects.Project",
        on_delete=models.CASCADE,
        related_name="interview_questions",
        null=True,
        blank=True,
    )

    question = models.TextField()

    category = models.CharField(
        max_length=50,
        choices=CATEGORY_CHOICES
    )

    difficulty = models.CharField(
        max_length=20,
        choices=DIFFICULTY_CHOICES
    )

    explanation = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        role_name = (
            self.target_role.name
            if self.target_role
            else "General"
        )

        return f"{role_name} - {self.question[:70]}"


class InterviewSession(models.Model):

    CONFIDENCE_CHOICES = [
        (1, "1 - Very Low"),
        (2, "2 - Low"),
        (3, "3 - Average"),
        (4, "4 - Good"),
        (5, "5 - Very High"),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="interview_sessions"
    )

    question = models.ForeignKey(
        InterviewQuestion,
        on_delete=models.CASCADE,
        related_name="practice_sessions"
    )

    confidence = models.PositiveSmallIntegerField(
        choices=CONFIDENCE_CHOICES
    )

    notes = models.TextField(blank=True)

    practiced_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return (
            f"{self.user.username} - "
            f"{self.question.question[:50]}"
        )