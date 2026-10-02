import re

from django.contrib.auth.models import User
from django.db import models

from skills.models import Skill


class JobAnalysis(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="job_analyses"
    )

    job_title = models.CharField(max_length=150)
    raw_description = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.job_title} ({self.user.username})"

    def extract_skills(self):
        """
        Scans raw_description for skills that exist in the Skill table.
        Skills found in a line/section mentioning "preferred" or "nice
        to have" are tagged preferred; everything else defaults to
        required. Best-effort only — never invents a skill that isn't
        already in the Skill table.
        """
        text = self.raw_description
        lower_text = text.lower()

        preferred_start = None
        for marker in ["preferred", "nice to have", "bonus"]:
            idx = lower_text.find(marker)
            if idx != -1:
                preferred_start = idx if preferred_start is None else min(preferred_start, idx)

        required_section = text[:preferred_start] if preferred_start else text
        preferred_section = text[preferred_start:] if preferred_start else ""

        required_skills = []
        preferred_skills = []

        for skill in Skill.objects.all():
            pattern = r'\b' + re.escape(skill.name.lower()) + r'\b'
            if re.search(pattern, preferred_section.lower()):
                preferred_skills.append(skill)
            elif re.search(pattern, required_section.lower()):
                required_skills.append(skill)

        return required_skills, preferred_skills


class JobSkill(models.Model):
    REQUIREMENT_CHOICES = [
        ("Required", "Required"),
        ("Preferred", "Preferred"),
    ]

    job_analysis = models.ForeignKey(
        JobAnalysis,
        on_delete=models.CASCADE,
        related_name="job_skills"
    )
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)

    requirement_type = models.CharField(
        max_length=10,
        choices=REQUIREMENT_CHOICES,
        default="Required"
    )

    class Meta:
        unique_together = ("job_analysis", "skill")

    def __str__(self):
        return f"{self.skill.name} ({self.requirement_type}) - {self.job_analysis.job_title}"