from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

from .models import Project
from skills.models import Skill


@login_required
def project_list(request):
    projects = Project.objects.filter(
        user=request.user
    ).prefetch_related("skills").order_by("-created_at")

    return render(
        request,
        "projects/project_list.html",
        {"projects": projects}
    )


@login_required
def add_project(request):
    if request.method == "POST":
        name = request.POST.get("name")
        description = request.POST.get("description")
        technologies = request.POST.get("technologies")
        github_url = request.POST.get("github_url")
        live_url = request.POST.get("live_url")
        status = request.POST.get("status")
        start_date = request.POST.get("start_date") or None
        end_date = request.POST.get("end_date") or None
        skill_ids = request.POST.getlist("skills")

        project = Project.objects.create(
            user=request.user,
            name=name,
            description=description,
            technologies=technologies,
            github_url=github_url,
            live_url=live_url,
            status=status,
            start_date=start_date,
            end_date=end_date,
        )

        if skill_ids:
            project.skills.set(skill_ids)

        return redirect("projects:project_list")

    skills = Skill.objects.all().order_by("name")

    prefill = {
        "name": request.GET.get("name", ""),
        "description": request.GET.get("description", ""),
        "technologies": request.GET.get("technologies", ""),
    }

    return render(
        request,
        "projects/add_project.html",
        {"skills": skills, "prefill": prefill}
    )


@login_required
def project_detail(request, project_id):
    project = get_object_or_404(
        Project, id=project_id, user=request.user
    )

    return render(
        request,
        "projects/project_detail.html",
        {"project": project}
    )


@login_required
def edit_project(request, project_id):
    project = get_object_or_404(
        Project, id=project_id, user=request.user
    )

    if request.method == "POST":
        project.name = request.POST.get("name")
        project.description = request.POST.get("description")
        project.technologies = request.POST.get("technologies")
        project.github_url = request.POST.get("github_url")
        project.live_url = request.POST.get("live_url")
        project.status = request.POST.get("status")
        project.start_date = request.POST.get("start_date") or None
        project.end_date = request.POST.get("end_date") or None
        project.save()

        skill_ids = request.POST.getlist("skills")
        project.skills.set(skill_ids)

        return redirect("projects:project_detail", project_id=project.id)

    skills = Skill.objects.all().order_by("name")
    selected_skill_ids = list(
        project.skills.values_list("id", flat=True)
    )

    return render(
        request,
        "projects/edit_project.html",
        {
            "project": project,
            "skills": skills,
            "selected_skill_ids": selected_skill_ids,
        }
    )


@login_required
def delete_project(request, project_id):
    project = get_object_or_404(
        Project, id=project_id, user=request.user
    )

    if request.method == "POST":
        project.delete()
        return redirect("projects:project_list")

    return render(
        request,
        "projects/delete_project.html",
        {"project": project}
    )