from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

from .models import JobAnalysis, JobSkill
from skills.models import UserSkill
from resume.models import Resume
from projects.models import Project


@login_required
def job_list(request):
    jobs = JobAnalysis.objects.filter(
        user=request.user
    ).order_by("-created_at")

    return render(
        request,
        "jobs/job_list.html",
        {
            "jobs": jobs,
        }
    )


@login_required
def add_job(request):

    if request.method == "POST":

        job_title = request.POST.get("job_title")
        raw_description = request.POST.get("raw_description")

        job = JobAnalysis.objects.create(
            user=request.user,
            job_title=job_title,
            raw_description=raw_description,
        )

        required_skills, preferred_skills = job.extract_skills()

        for skill in required_skills:
            JobSkill.objects.create(
                job_analysis=job,
                skill=skill,
                requirement_type="Required",
            )

        for skill in preferred_skills:
            JobSkill.objects.create(
                job_analysis=job,
                skill=skill,
                requirement_type="Preferred",
            )

        return redirect(
            "jobs:job_detail",
            job_id=job.id,
        )

    return render(
        request,
        "jobs/add_job.html"
    )


@login_required
def reanalyze_job(request, job_id):

    job = get_object_or_404(
        JobAnalysis,
        id=job_id,
        user=request.user,
    )

    if request.method == "POST":

        # Remove previous extracted skills
        job.job_skills.all().delete()

        # Extract again
        required_skills, preferred_skills = job.extract_skills()

        for skill in required_skills:
            JobSkill.objects.create(
                job_analysis=job,
                skill=skill,
                requirement_type="Required",
            )

        for skill in preferred_skills:
            JobSkill.objects.create(
                job_analysis=job,
                skill=skill,
                requirement_type="Preferred",
            )

    return redirect(
        "jobs:job_detail",
        job_id=job.id,
    )


def _evaluate_skill_match(user, skill):

    # -----------------------------------------
    # 1. Check user's tracked skill
    # -----------------------------------------

    user_skill = UserSkill.objects.filter(
        user=user,
        skill=skill,
    ).first()

    if user_skill:

        if user_skill.level in [
            "Intermediate",
            "Advanced",
        ]:
            status = "Matched"

        elif user_skill.level == "Beginner":
            status = "Partial"

        else:
            status = "Missing"

    else:
        status = "Missing"


    # -----------------------------------------
    # 2. Check resume
    # -----------------------------------------

    resume = Resume.objects.filter(
        user=user
    ).first()

    in_resume = False

    if resume:
        in_resume = resume.detected_skills.filter(
            id=skill.id
        ).exists()


    # -----------------------------------------
    # 3. Check projects
    # -----------------------------------------

    demonstrating_projects = Project.objects.filter(
        user=user,
        skills=skill,
    ).distinct()


    # -----------------------------------------
    # 4. Create suggestion
    # -----------------------------------------

    suggestion = None

    if status == "Missing":

        existing_projects = Project.objects.filter(
            user=user
        ).exclude(
            skills=skill
        )

        if existing_projects.exists():

            closest_project = existing_projects.order_by(
                "-created_at"
            ).first()

            suggestion = (
                f'Consider adding {skill.name} functionality '
                f'to "{closest_project.name}" to practice this requirement.'
            )

        else:

            suggestion = (
                f"Consider starting a small project "
                f"to practice {skill.name}."
            )


    # -----------------------------------------
    # 5. Return complete match information
    # -----------------------------------------

    return {
        "skill": skill,
        "status": status,
        "user_skill": user_skill,
        "in_resume": in_resume,
        "projects": demonstrating_projects,
        "suggestion": suggestion,
    }


@login_required
def job_detail(request, job_id):

    job = get_object_or_404(
        JobAnalysis,
        id=job_id,
        user=request.user,
    )

    required_skills = job.job_skills.filter(
        requirement_type="Required"
    )

    preferred_skills = job.job_skills.filter(
        requirement_type="Preferred"
    )

    return render(
        request,
        "jobs/job_detail.html",
        {
            "job": job,
            "required_skills": required_skills,
            "preferred_skills": preferred_skills,
        }
    )


@login_required
def job_match(request, job_id):

    job = get_object_or_404(
        JobAnalysis,
        id=job_id,
        user=request.user,
    )

    # -----------------------------------------
    # Required skills
    # -----------------------------------------

    required = job.job_skills.filter(
        requirement_type="Required"
    )

    required_results = [
        _evaluate_skill_match(
            request.user,
            job_skill.skill,
        )
        for job_skill in required
    ]


    # -----------------------------------------
    # Preferred skills
    # -----------------------------------------

    preferred = job.job_skills.filter(
        requirement_type="Preferred"
    )

    preferred_results = [
        _evaluate_skill_match(
            request.user,
            job_skill.skill,
        )
        for job_skill in preferred
    ]


    # -----------------------------------------
    # Required skill counts
    # -----------------------------------------

    matched_count = sum(
        1
        for result in required_results
        if result["status"] == "Matched"
    )

    partial_count = sum(
        1
        for result in required_results
        if result["status"] == "Partial"
    )

    missing_count = sum(
        1
        for result in required_results
        if result["status"] == "Missing"
    )


    # -----------------------------------------
    # Match percentage
    # -----------------------------------------

    total_required = len(required_results)

    if total_required:

        match_percentage = round(
            (
                matched_count
                + (partial_count * 0.5)
            )
            / total_required
            * 100,
            1,
        )

    else:

        match_percentage = 0


    return render(
        request,
        "jobs/job_match.html",
        {
            "job": job,

            "required_results": required_results,
            "preferred_results": preferred_results,

            "matched_count": matched_count,
            "partial_count": partial_count,
            "missing_count": missing_count,

            "total_required": total_required,
            "match_percentage": match_percentage,
        }
    )


@login_required
def delete_job(request, job_id):

    job = get_object_or_404(
        JobAnalysis,
        id=job_id,
        user=request.user,
    )

    if request.method == "POST":

        job.delete()

        return redirect(
            "jobs:job_list"
        )

    return render(
        request,
        "jobs/delete_job.html",
        {
            "job": job,
        }
    )