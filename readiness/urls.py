from django.urls import path

from . import views

app_name = "readiness"

urlpatterns = [
    path("<int:job_id>/", views.readiness_detail, name="readiness_detail"),
]