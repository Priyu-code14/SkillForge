from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.db.models import Avg
from django.shortcuts import redirect, render

from skills.models import UserSkill
from interviews.models import InterviewSession
from jobs.models import JobAnalysis
from readiness.models import ReadinessSnapshot


def home(request):
    return render(request, "accounts/home.html")


def register(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")

        if User.objects.filter(username=username).exists():
            return render(
                request,
                "accounts/register.html",
                {"error": "Username already exists."}
            )

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        login(request, user)

        return redirect("accounts:dashboard")

    return render(request, "accounts/register.html")


def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:
            login(request, user)
            return redirect("accounts:dashboard")

        return render(
            request,
            "accounts/login.html",
            {"error": "Invalid username or password."}
        )

    return render(request, "accounts/login.html")


def logout_view(request):
    logout(request)
    return redirect("home")


def dashboard(request):

    if not request.user.is_authenticated:
        return redirect("accounts:login")

    # =====================================================
    # USER SKILLS
    # =====================================================

    user_skills = (
        UserSkill.objects
        .filter(user=request.user)
        .select_related("skill")
    )

    # =====================================================
    # TARGET ROLE
    # =====================================================

    profile = getattr(request.user, "profile", None)

    target_role = None

    if profile:
        target_role = profile.target_role

    # =====================================================
    # PROJECTS
    # =====================================================

    projects = request.user.projects.all()

    total_projects = projects.count()

    completed_projects = projects.filter(
        status="Completed"
    ).count()

    # =====================================================
    # INTERVIEW PREPARATION
    # =====================================================

    interview_sessions = (
        InterviewSession.objects
        .filter(user=request.user)
    )

    total_practiced = interview_sessions.count()

    # =====================================================
    # AVERAGE INTERVIEW CONFIDENCE
    # =====================================================

    average_confidence = interview_sessions.aggregate(
        average=Avg("confidence")
    )["average"]

    if average_confidence is not None:
        average_confidence = round(
            average_confidence,
            1
        )

    # =====================================================
    # LATEST READINESS SNAPSHOT
    # =====================================================

    latest_readiness = (
        ReadinessSnapshot.objects
        .filter(user=request.user)
        .select_related("job_analysis")
        .order_by("-created_at")
        .first()
    )

    readiness_score = None
    readiness_job = None

    if latest_readiness:
        readiness_score = latest_readiness.total_score
        readiness_job = latest_readiness.job_analysis

    # =====================================================
    # LATEST JOB ANALYSIS
    # =====================================================

    latest_job = (
        JobAnalysis.objects
        .filter(user=request.user)
        .order_by("-created_at")
        .first()
    )

    # =====================================================
    # DASHBOARD CONTEXT
    # =====================================================

    context = {

        # Skills
        "user_skills": user_skills,

        # Target role
        "target_role": target_role,

        # Projects
        "projects": projects,
        "total_projects": total_projects,
        "completed_projects": completed_projects,

        # Interviews
        "total_practiced": total_practiced,
        "interview_sessions": total_practiced,
        "average_confidence": average_confidence,

        # Readiness
        "readiness_score": readiness_score,
        "readiness_job": readiness_job,

        # Job Analysis
        "latest_job": latest_job,

        # Dashboard template compatibility
        "project_count": total_projects,
        "completed_project_count": completed_projects,
        "interview_count": total_practiced,
    }

    return render(
        request,
        "accounts/dashboard.html",
        context
    )