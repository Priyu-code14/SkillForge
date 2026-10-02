from django.urls import path

from . import views

app_name = "roadmap"

urlpatterns = [
    path("", views.roadmap_home, name="roadmap_home"),
    path("<int:job_id>/", views.roadmap_detail, name="roadmap_detail"),
    path("<int:job_id>/generate/", views.generate_roadmap, name="generate_roadmap"),
    path("goal/<int:goal_id>/status/", views.update_goal_status, name="update_goal_status"),
]