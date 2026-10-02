"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from accounts.views import home


urlpatterns = [
    path("", home, name="home"),
    path("accounts/", include("accounts.urls")),
    path("skills/", include("skills.urls")),
    path("projects/", include("projects.urls")),
    path("resume/", include("resume.urls")),
    path("jobs/", include("jobs.urls")),
    path("readiness/", include("readiness.urls")),
    path("roadmap/", include("roadmap.urls")),
    path("interviews/", include("interviews.urls")),
    path("admin/", admin.site.urls),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)