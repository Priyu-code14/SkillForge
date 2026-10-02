from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.db.models import Avg

from jobs.models import JobAnalysis
from jobs.views import _evaluate_skill_match
from projects.models import Project
from interviews.models import InterviewSession

from .models import ReadinessSnapshot


@login_required
def readiness_detail(request, job_id):

    job = get_object_or_404(
        JobAnalysis,
        id=job_id,
        user=request.user
    )

    # =========================================================
    # 1. SKILL SCORE
    # =========================================================

    required = job.job_skills.filter(
        requirement_type="Required"
    )

    required_results = [
        _evaluate_skill_match(request.user, js.skill)
        for js in required
    ]

    matched_count = sum(
        1 for r in required_results
        if r["status"] == "Matched"
    )

    partial_count = sum(
        1 for r in required_results
        if r["status"] == "Partial"
    )

    missing_count = sum(
        1 for r in required_results
        if r["status"] == "Missing"
    )

    total_required = len(required_results)

    if total_required > 0:
        skill_score = round(
            (
                matched_count * 1.0
                + partial_count * 0.5
            )
            / total_required
            * 100,
            1
        )
    else:
        skill_score = 0


    # =========================================================
    # 2. PROJECT SCORE
    # =========================================================

    required_skill_ids = [
        r["skill"].id
        for r in required_results
    ]

    relevant_projects = Project.objects.filter(
        user=request.user,
        skills__id__in=required_skill_ids
    ).distinct()

    covered_skill_ids = set()

    for project in relevant_projects:

        covered_skill_ids.update(
            project.skills.filter(
                id__in=required_skill_ids
            ).values_list(
                "id",
                flat=True
            )
        )

    missing_project_experience = (
        total_required - len(covered_skill_ids)
    )

    if total_required > 0:

        project_score = round(
            len(covered_skill_ids)
            / total_required
            * 100,
            1
        )

    else:

        project_score = 0


    # =========================================================
    # 3. INTERVIEW SCORE
    # =========================================================

    interview_sessions = InterviewSession.objects.filter(
        user=request.user
    )

    interview_count = interview_sessions.count()

    average_confidence = interview_sessions.aggregate(
        average=Avg("confidence")
    )["average"]

    if average_confidence is not None:

        average_confidence = round(
            average_confidence,
            1
        )

        interview_score = round(
            (average_confidence / 5) * 100,
            1
        )

    else:

        average_confidence = 0
        interview_score = 0


        # =========================================================
    # 4. RESUME / PORTFOLIO SCORE
    # =========================================================

    from resume.models import Resume

    resume = Resume.objects.filter(
        user=request.user
    ).first()

    if resume:
        # Check how many required skills are detected in the resume
        resume_skill_ids = set(
            resume.detected_skills.values_list(
                "id",
                flat=True
            )
        )

        if total_required > 0:
            resume_matched_count = sum(
                1
                for skill_id in required_skill_ids
                if skill_id in resume_skill_ids
            )

            portfolio_score = round(
                resume_matched_count
                / total_required
                * 100,
                1
            )
        else:
            portfolio_score = 0

    else:
        portfolio_score = 0


    # =========================================================
    # 5. OVERALL READINESS
    # =========================================================

    total_score = round(
        (
            skill_score * 0.35
            + project_score * 0.25
            + interview_score * 0.20
            + portfolio_score * 0.20
        ),
        1
    )

    # =========================================================
    # 6. SAVE READINESS SNAPSHOT
    # =========================================================

    snapshot = ReadinessSnapshot.objects.create(
        user=request.user,
        job_analysis=job,
        skill_score=skill_score,
        project_score=project_score,
        interview_score=interview_score,
        portfolio_score=portfolio_score,
        total_score=total_score,
    )


    # =========================================================
    # 7. SEND DATA TO TEMPLATE
    # =========================================================

    context = {

        "job": job,

        # Skill data
        "matched_count": matched_count,
        "partial_count": partial_count,
        "missing_count": missing_count,
        "total_required": total_required,

        # Project data
        "relevant_projects": relevant_projects,
        "missing_project_experience": missing_project_experience,

        # Interview data
        "interview_count": interview_count,
        "average_confidence": average_confidence,

        # Snapshot
        "snapshot": snapshot,
    }


    return render(
        request,
        "readiness/readiness_detail.html",
        context
    )