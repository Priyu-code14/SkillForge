from django.contrib.auth.models import User
from django.db import models

from skills.models import Skill


class Project(models.Model):
    STATUS_CHOICES = [
        ("Planning", "Planning"),
        ("In Progress", "In Progress"),
        ("Completed", "Completed"),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="projects"
    )
    name = models.CharField(max_length=150)
    description = models.TextField()

    technologies = models.TextField(
        blank=True,
        help_text="Example: Python, Django, MySQL"
    )

    github_url = models.URLField(blank=True)
    live_url = models.URLField(blank=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="Planning"
    )

    skills = models.ManyToManyField(
        Skill,
        blank=True,
        related_name="projects"
    )

    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)

    imported_from_resume = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name