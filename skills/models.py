from django.contrib.auth.models import User
from django.db import models

from accounts.models import TargetRole


class Skill(models.Model):
    CATEGORY_CHOICES = [
        ("Programming", "Programming"),
        ("Frontend", "Frontend"),
        ("Backend", "Backend"),
        ("Database", "Database"),
        ("Tools", "Tools"),
        ("Other", "Other"),
    ]

    name = models.CharField(max_length=100, unique=True)
    category = models.CharField(
        max_length=50,
        choices=CATEGORY_CHOICES
    )
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class RoleSkill(models.Model):
    role = models.ForeignKey(
        TargetRole,
        on_delete=models.CASCADE,
        related_name="role_skills"
    )
    skill = models.ForeignKey(
        Skill,
        on_delete=models.CASCADE,
        related_name="role_requirements"
    )
    required_level = models.PositiveIntegerField()
    weight = models.FloatField(default=1.0)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["role", "skill"],
                name="unique_role_skill"
            )
        ]

    def __str__(self):
        return f"{self.role.name} - {self.skill.name}"


class UserSkill(models.Model):
    LEVEL_CHOICES = [
        ("Beginner", "Beginner"),
        ("Intermediate", "Intermediate"),
        ("Advanced", "Advanced"),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="user_skills"
    )
    skill = models.ForeignKey(
        Skill,
        on_delete=models.CASCADE,
        related_name="user_skills"
    )
    level = models.CharField(
        max_length=20,
        choices=LEVEL_CHOICES
    )
    score = models.PositiveIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "skill"],
                name="unique_user_skill"
            )
        ]

    def __str__(self):
        return f"{self.user.username} - {self.skill.name}"