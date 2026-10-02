from django.urls import path

from . import views

app_name = "jobs"

urlpatterns = [
    path("", views.job_list, name="job_list"),
    path("add/", views.add_job, name="add_job"),
    path("<int:job_id>/reanalyze/", views.reanalyze_job, name="reanalyze_job"),
    path("<int:job_id>/", views.job_detail, name="job_detail"),
    path("<int:job_id>/match/", views.job_match, name="job_match"),
    path("<int:job_id>/delete/", views.delete_job, name="delete_job"),
]