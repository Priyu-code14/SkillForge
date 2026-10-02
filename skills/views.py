from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from .models import Skill, UserSkill


@login_required
def skill_list(request):
    user_skills = UserSkill.objects.filter(
        user=request.user
    ).select_related("skill")

    return render(
        request,
        "skills/skill_list.html",
        {"user_skills": user_skills}
    )


@login_required
def add_skill(request):
    if request.method == "POST":
        skill_id = request.POST.get("skill")
        level = request.POST.get("level")

        skill = Skill.objects.get(id=skill_id)

        level_scores = {
            "Beginner": 30,
            "Intermediate": 60,
            "Advanced": 90,
        }

        score = level_scores.get(level, 0)

        UserSkill.objects.update_or_create(
            user=request.user,
            skill=skill,
            defaults={
                "level": level,
                "score": score,
            }
        )

        return redirect("skills:skill_list")

    skills = Skill.objects.all().order_by("name")

    return render(
        request,
        "skills/add_skill.html",
        {"skills": skills}
    )