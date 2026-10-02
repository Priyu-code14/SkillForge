from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Count
from django.shortcuts import get_object_or_404, redirect, render

from .models import InterviewQuestion, InterviewSession


@login_required
def interview_home(request):
    """
    Interview preparation home page.

    Shows questions related to the user's selected target role.
    If role-specific questions are not available, general questions
    are shown as a fallback.
    """

    profile = getattr(request.user, "profile", None)

    target_role = None

    if profile:
        target_role = profile.target_role

    # ---------------------------------------------------------
    # Get role-specific questions
    # ---------------------------------------------------------
    if target_role:
        questions = InterviewQuestion.objects.filter(
            target_role=target_role
        ).order_by("difficulty", "created_at")

    else:
        questions = InterviewQuestion.objects.none()

    # ---------------------------------------------------------
    # Fallback to general questions
    # ---------------------------------------------------------
    if not questions.exists():
        questions = InterviewQuestion.objects.filter(
            target_role__isnull=True,
            project__isnull=True
        ).order_by("difficulty", "created_at")

    # ---------------------------------------------------------
    # User's interview progress
    # ---------------------------------------------------------
    practiced_sessions = InterviewSession.objects.filter(
        user=request.user
    )

    total_practiced = practiced_sessions.count()

    average_confidence = practiced_sessions.aggregate(
        average=Avg("confidence")
    )["average"]

    if average_confidence is not None:
        average_confidence = round(average_confidence, 1)

    # ---------------------------------------------------------
    # Category-wise progress
    # ---------------------------------------------------------
    category_progress = (
        practiced_sessions
        .values("question__category")
        .annotate(
            practiced=Count("id")
        )
        .order_by("question__category")
    )

    context = {
        "target_role": target_role,
        "questions": questions,
        "total_practiced": total_practiced,
        "average_confidence": average_confidence,
        "category_progress": category_progress,
    }

    return render(
        request,
        "interviews/interview_home.html",
        context
    )


@login_required
def practice_question(request, question_id):
    """
    Display one interview question and save the user's
    confidence level and notes after practice.
    """

    question = get_object_or_404(
        InterviewQuestion,
        id=question_id
    )

    # ---------------------------------------------------------
    # User's target role
    # ---------------------------------------------------------
    profile = getattr(request.user, "profile", None)

    target_role = None

    if profile:
        target_role = profile.target_role

    # ---------------------------------------------------------
    # Security check for role-specific questions
    # ---------------------------------------------------------
    if (
        question.target_role is not None
        and question.target_role != target_role
    ):
        return redirect("interviews:interview_home")

    # ---------------------------------------------------------
    # Security check for project-specific questions
    # ---------------------------------------------------------
    if question.project is not None:

        if question.project.user != request.user:
            return redirect("interviews:interview_home")

    # ---------------------------------------------------------
    # Save practice session
    # ---------------------------------------------------------
    if request.method == "POST":

        confidence = request.POST.get("confidence")
        notes = request.POST.get("notes", "").strip()

        if confidence:

            try:
                confidence_value = int(confidence)

                if 1 <= confidence_value <= 5:

                    InterviewSession.objects.create(
                        user=request.user,
                        question=question,
                        confidence=confidence_value,
                        notes=notes,
                    )

                    return redirect(
                        "interviews:interview_progress"
                    )

            except (TypeError, ValueError):
                pass

    context = {
        "question": question,
        "target_role": target_role,
    }

    return render(
        request,
        "interviews/practice_question.html",
        context
    )


@login_required
def interview_progress(request):
    """
    Display the user's interview preparation progress.
    """

    sessions = (
        InterviewSession.objects
        .filter(user=request.user)
        .select_related(
            "question",
            "question__project"
        )
        .order_by("-practiced_at")
    )

    total_practiced = sessions.count()

    average_confidence = sessions.aggregate(
        average=Avg("confidence")
    )["average"]

    if average_confidence is not None:
        average_confidence = round(average_confidence, 1)

    # ---------------------------------------------------------
    # Progress by interview category
    # ---------------------------------------------------------
    category_progress = (
        sessions
        .values("question__category")
        .annotate(
            practiced=Count("id")
        )
        .order_by("question__category")
    )

    # ---------------------------------------------------------
    # Progress by difficulty
    # ---------------------------------------------------------
    difficulty_progress = (
        sessions
        .values("question__difficulty")
        .annotate(
            practiced=Count("id")
        )
        .order_by("question__difficulty")
    )

    context = {
        "sessions": sessions,
        "total_practiced": total_practiced,
        "average_confidence": average_confidence,
        "category_progress": category_progress,
        "difficulty_progress": difficulty_progress,
    }

    return render(
        request,
        "interviews/interview_progress.html",
        context
    )


@login_required
def skill_questions(request):
    """
    Show interview questions related to the user's skills.
    """

    # Get the user's skills
    user_skills = (
        request.user.user_skills
        .select_related("skill")
        .all()
    )

    # Extract skill names
    skill_names = [
        user_skill.skill.name
        for user_skill in user_skills
    ]

    # Match skill names with interview question categories
    questions = (
        InterviewQuestion.objects
        .filter(
            category__in=skill_names,
            project__isnull=True
        )
        .order_by(
            "difficulty",
            "created_at"
        )
    )

    context = {
        "questions": questions,
        "user_skills": user_skills,
    }

    return render(
        request,
        "interviews/skill_questions.html",
        context
    )


@login_required
def project_questions(request):
    """
    Show interview questions related to the user's projects.
    """

    # Only show projects belonging to the logged-in user
    projects = request.user.projects.all()

    # Only show questions attached to the user's projects
    questions = (
        InterviewQuestion.objects
        .filter(
            project__user=request.user
        )
        .select_related("project")
        .order_by(
            "difficulty",
            "created_at"
        )
    )

    context = {
        "projects": projects,
        "questions": questions,
    }

    return render(
        request,
        "interviews/project_questions.html",
        context
    )