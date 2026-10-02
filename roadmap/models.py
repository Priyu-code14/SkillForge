from django.contrib.auth.models import User
from django.db import models

from jobs.models import JobAnalysis
from skills.models import Skill


class SkillStepTemplate(models.Model):
    PHASE_CHOICES = [
        ("Learn", "Learn"),
        ("Practice", "Practice"),
        ("Project", "Project"),
    ]

    skill = models.ForeignKey(
        Skill,
        on_delete=models.CASCADE,
        related_name="step_templates"
    )
    phase = models.CharField(
        max_length=10,
        choices=PHASE_CHOICES,
        default="Learn"
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["skill__name", "order"]

    def __str__(self):
        return f"{self.skill.name} - {self.phase}: {self.title}"


class Goal(models.Model):
    STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("In Progress", "In Progress"),
        ("Completed", "Completed"),
    ]

    PRIORITY_CHOICES = [
        ("Low", "Low"),
        ("Medium", "Medium"),
        ("High", "High"),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="goals"
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="Pending"
    )

    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default="Medium"
    )

    due_date = models.DateField(null=True, blank=True)

    job_analysis = models.ForeignKey(
        JobAnalysis,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="goals"
    )
    skill = models.ForeignKey(
        Skill,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="goals"
    )
    phase = models.CharField(max_length=10, blank=True)
    order = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title