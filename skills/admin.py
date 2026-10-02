from django.contrib import admin

from .models import Skill, RoleSkill, UserSkill

admin.site.register(Skill)
admin.site.register(RoleSkill)
admin.site.register(UserSkill)