from django.urls import path

from . import views

app_name = "projects"

urlpatterns = [
    path("", views.project_list, name="project_list"),
    path("add/", views.add_project, name="add_project"),
    path("<int:project_id>/", views.project_detail, name="project_detail"),
    path("<int:project_id>/edit/", views.edit_project, name="edit_project"),
    path("<int:project_id>/delete/", views.delete_project, name="delete_project"),
]