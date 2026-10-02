from django.core.management.base import BaseCommand

from roadmap.models import SkillStepTemplate
from skills.models import Skill

STEPS = {
    "Python": [
        ("Learn", "Revise Python core concepts", "OOP, exception handling, data structures and file handling."),
        ("Practice", "Solve small Python exercises", "Write short programs using lists, dictionaries, classes and file I/O."),
        ("Project", "Add a feature to a Python project", "Extend an existing project with a new module or input validation."),
    ],
    "SQL": [
        ("Learn", "Learn core SQL queries", "SELECT, WHERE, ORDER BY, JOIN, GROUP BY and subqueries."),
        ("Practice", "Practice SQL problems", "Solve JOIN and GROUP BY exercises on a sample database."),
        ("Project", "Write SQL queries for a project", "Create reporting queries against your project's database."),
    ],
    "MySQL": [
        ("Learn", "Learn MySQL basics", "Databases, tables, primary and foreign keys, indexes and relationships."),
        ("Practice", "Practice MySQL queries", "Insert, update and query data using the MySQL client."),
        ("Project", "Connect MySQL to an application", "Store and read a project's data from MySQL."),
    ],
    "Django": [
        ("Learn", "Learn Django fundamentals", "Models, views, URLs, templates, the ORM and authentication."),
        ("Practice", "Build small Django pages", "Create list, add, edit and delete pages for one model."),
        ("Project", "Build a login-protected Django feature", "Add user-specific pages to a project."),
    ],
    "FastAPI": [
        ("Learn", "Learn FastAPI basics", "Path operations, request and response models, and dependencies."),
        ("Practice", "Build small FastAPI endpoints", "Create GET and POST endpoints and try them in the built-in docs page."),
        ("Project", "Build a FastAPI service", "Expose an existing project's data through a FastAPI backend."),
    ],
    "REST API": [
        ("Learn", "Learn REST principles", "HTTP methods, status codes, JSON and resource-based URLs."),
        ("Practice", "Call and test APIs", "Send requests to a public API using Postman or curl."),
        ("Project", "Build a REST API", "Add REST endpoints to an existing project."),
    ],
    "AWS": [
        ("Learn", "Learn AWS core services", "IAM, EC2, S3 and RDS basics."),
        ("Practice", "Try the AWS free tier", "Launch a small instance or upload files to S3."),
        ("Project", "Deploy a small app on AWS", "Host a simple project on a free-tier service."),
    ],
    "Azure": [
        ("Learn", "Learn Azure core services", "Virtual Machines, Storage accounts and App Service basics."),
        ("Practice", "Try the Azure free account", "Create a small resource group and upload a file to storage."),
        ("Project", "Deploy a small app on Azure", "Host a simple project on Azure App Service."),
    ],
    "Google Cloud": [
        ("Learn", "Learn Google Cloud core services", "Compute Engine, Cloud Storage and Cloud Run basics."),
        ("Practice", "Try the Google Cloud free tier", "Create a bucket and upload a file."),
        ("Project", "Deploy a small app on Google Cloud", "Host a simple project on Cloud Run."),
    ],
    "Git": [
        ("Learn", "Learn Git basics", "Commit, branch, merge and working with a remote repository."),
        ("Practice", "Practice branches and merge conflicts", "Create a branch, change the same file twice and resolve the conflict."),
        ("Project", "Publish a project repository", "Push a project to GitHub with clear commit messages."),
    ],
    "JavaScript": [
        ("Learn", "Learn JavaScript fundamentals", "Variables, functions, the DOM and events."),
        ("Practice", "Practice small DOM exercises", "Build a counter, a to-do list and a form validator."),
        ("Project", "Add interactivity to a web page", "Use JavaScript to filter or update content on a project page."),
    ],
}


class Command(BaseCommand):
    help = "Add starter roadmap steps for common skills (safe to run again)."

    def handle(self, *args, **options):
        created = 0
        skipped = []

        for skill_name, steps in STEPS.items():
            skill = Skill.objects.filter(name__iexact=skill_name).first()
            if not skill:
                skipped.append(skill_name)
                continue

            for order, (phase, title, description) in enumerate(steps, start=1):
                _, was_created = SkillStepTemplate.objects.get_or_create(
                    skill=skill,
                    title=title,
                    defaults={
                        "phase": phase,
                        "description": description,
                        "order": order,
                    },
                )
                if was_created:
                    created += 1

        self.stdout.write(self.style.SUCCESS(f"Added {created} step(s)."))
        if skipped:
            self.stdout.write("Skipped (not in your Skill table): " + ", ".join(skipped))