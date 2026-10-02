from django.contrib import admin

from .models import Goal, SkillStepTemplate


@admin.register(SkillStepTemplate)
class SkillStepTemplateAdmin(admin.ModelAdmin):
    list_display = ("skill", "phase", "order", "title")
    list_filter = ("skill", "phase")
    ordering = ("skill__name", "order")


admin.site.register(Goal)