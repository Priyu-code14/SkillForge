from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

from jobs.models import JobAnalysis
from jobs.views import _evaluate_skill_match

from .models import Goal, SkillStepTemplate


def _generic_steps(skill_name):
    return [
        ("Learn", f"Learn {skill_name} fundamentals", f"Study the core concepts of {skill_name}."),
        ("Practice", f"Practice {skill_name} with small exercises", f"Complete short hands-on exercises using {skill_name}."),
        ("Project", f"Build a mini project using {skill_name}", f"Apply {skill_name} in a small project or an existing one."),
    ]

@login_required
def roadmap_home(request):
    jobs = JobAnalysis.objects.filter(
        user=request.user
    ).order_by("-created_at")

    return render(
        request,
        "roadmap/roadmap_home.html",
        {
            "jobs": jobs,
        }
    )


@login_required
def generate_roadmap(request, job_id):
    job = get_object_or_404(JobAnalysis, id=job_id, user=request.user)

    if request.method == "POST":
        order = Goal.objects.filter(user=request.user, job_analysis=job).count()

        for js in job.job_skills.filter(requirement_type="Required"):
            result = _evaluate_skill_match(request.user, js.skill)

            if result["status"] == "Matched":
                continue

            priority = "High" if result["status"] == "Missing" else "Medium"

            templates = SkillStepTemplate.objects.filter(skill=js.skill).order_by("order")
            if templates.exists():
                steps = [(t.phase, t.title, t.description) for t in templates]
            else:
                steps = _generic_steps(js.skill.name)

            for phase, title, description in steps:
                already_exists = Goal.objects.filter(
                    user=request.user,
                    job_analysis=job,
                    skill=js.skill,
                    title=title,
                ).exists()
                if already_exists:
                    continue

                order += 1
                Goal.objects.create(
                    user=request.user,
                    job_analysis=job,
                    skill=js.skill,
                    title=title,
                    description=description,
                    phase=phase,
                    priority=priority,
                    order=order,
                )

    return redirect("roadmap:roadmap_detail", job_id=job.id)


@login_required
def roadmap_detail(request, job_id):
    job = get_object_or_404(JobAnalysis, id=job_id, user=request.user)

    goals = Goal.objects.filter(
        user=request.user, job_analysis=job
    ).select_related("skill").order_by("order")

    groups = []
    for goal in goals:
        name = goal.skill.name if goal.skill else "General"
        if groups and groups[-1]["name"] == name:
            groups[-1]["goals"].append(goal)
        else:
            groups.append({"name": name, "priority": goal.priority, "goals": [goal]})

    total = goals.count()
    completed = goals.filter(status="Completed").count()
    progress = round(completed / total * 100, 1) if total else 0
    next_goal = goals.exclude(status="Completed").first()

    return render(
        request,
        "roadmap/roadmap_detail.html",
        {
            "job": job,
            "groups": groups,
            "total": total,
            "completed": completed,
            "progress": progress,
            "next_goal": next_goal,
            "status_choices": [c[0] for c in Goal.STATUS_CHOICES],
        }
    )


@login_required
def update_goal_status(request, goal_id):
    goal = get_object_or_404(Goal, id=goal_id, user=request.user)

    if request.method == "POST":
        status = request.POST.get("status")
        if status in dict(Goal.STATUS_CHOICES):
            goal.status = status
            goal.save()

    if goal.job_analysis_id:
        return redirect("roadmap:roadmap_detail", job_id=goal.job_analysis_id)
    return redirect("accounts:dashboard")