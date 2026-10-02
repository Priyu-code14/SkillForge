from django.contrib.auth.models import User
from django.db import models

from jobs.models import JobAnalysis


class ReadinessSnapshot(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="readiness_snapshots"
    )

    job_analysis = models.ForeignKey(
        JobAnalysis,
        on_delete=models.CASCADE,
        related_name="readiness_snapshots"
    )

    skill_score = models.FloatField()
    project_score = models.FloatField()
    interview_score = models.FloatField(default=0)
    portfolio_score = models.FloatField(default=0)

    total_score = models.FloatField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.job_analysis.job_title} - {self.total_score}%"