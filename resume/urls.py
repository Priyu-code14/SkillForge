from django.urls import path

from . import views

app_name = "resume"

urlpatterns = [
    path("", views.upload_resume, name="upload_resume"),
    path("skills/<int:skill_id>/add/", views.add_suggested_skill, name="add_suggested_skill"),
]