from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect

from .models import Resume
from skills.models import Skill, UserSkill
from projects.models import Project

ALLOWED_EXTENSIONS = [".pdf", ".docx"]

LEVEL_SCORES = {
    "Beginner": 30,
    "Intermediate": 60,
    "Advanced": 90,
}


def _match_skills_in_text(text):
    text_lower = text.lower()
    matched = []
    for skill in Skill.objects.all():
        if skill.name.lower() in text_lower:
            matched.append(skill)
    return matched


def _auto_add_projects(user, project_blocks):
    added = []
    for block in project_blocks:
        title = block["title"].strip()
        if not title:
            continue

        if Project.objects.filter(user=user, name__iexact=title).exists():
            continue

        project = Project.objects.create(
            user=user,
            name=title,
            description=block["description"],
            technologies=block["technologies"],
            imported_from_resume=True,
        )

        matched_skills = _match_skills_in_text(
            block["technologies"] + " " + block["description"]
        )
        if matched_skills:
            project.skills.set(matched_skills)

        added.append(project)

    return added


@login_required
def upload_resume(request):
    resume = Resume.objects.filter(user=request.user).first()

    if request.method == "POST":
        uploaded_file = request.FILES.get("file")

        if not uploaded_file:
            messages.error(request, "Please choose a file to upload.")
        else:
            filename = uploaded_file.name.lower()
            if not any(filename.endswith(ext) for ext in ALLOWED_EXTENSIONS):
                messages.error(request, "Only PDF or DOCX files are allowed.")
            else:
                if resume:
                    resume.file = uploaded_file
                    resume.original_filename = uploaded_file.name
                else:
                    resume = Resume(
                        user=request.user,
                        file=uploaded_file,
                        original_filename=uploaded_file.name,
                    )

                resume.save()

                extracted = resume.extract_text()
                resume.extracted_text = extracted
                resume.projects_text = resume.parse_projects_text() if extracted else ""
                resume.save()

                if extracted:
                    matched_skills = resume.parse_matched_skills()
                    resume.detected_skills.set(matched_skills)

                    project_blocks = resume.parse_project_blocks()
                    newly_added_projects = _auto_add_projects(request.user, project_blocks)

                    summary = "Resume uploaded and parsed."
                    if newly_added_projects:
                        summary += f" {len(newly_added_projects)} new project(s) added."
                    messages.success(request, summary)
                else:
                    resume.detected_skills.clear()
                    messages.error(request, "Resume uploaded, but no text could be extracted from this file.")

                return redirect("resume:upload_resume")

    project_blocks = resume.parse_project_blocks() if resume and resume.projects_text else []

    tracked_skill_ids = set()
    suggested_skills = []
    if resume:
        tracked_skill_ids = set(
            UserSkill.objects.filter(user=request.user).values_list("skill_id", flat=True)
        )
        suggested_skills = [
            s for s in resume.detected_skills.all() if s.id not in tracked_skill_ids
        ]

    return render(
        request,
        "resume/upload_resume.html",
        {
            "resume": resume,
            "project_blocks": project_blocks,
            "suggested_skills": suggested_skills,
        }
    )


@login_required
def add_suggested_skill(request, skill_id):
    if request.method == "POST":
        skill = Skill.objects.filter(id=skill_id).first()
        level = request.POST.get("level", "Beginner")

        if skill and level in LEVEL_SCORES:
            if not UserSkill.objects.filter(user=request.user, skill=skill).exists():
                UserSkill.objects.create(
                    user=request.user,
                    skill=skill,
                    level=level,
                    score=LEVEL_SCORES[level],
                )
                messages.success(request, f"{skill.name} added to your skills.")

    return redirect("resume:upload_resume")