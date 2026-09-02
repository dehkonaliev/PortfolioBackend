from django.contrib import admin
from .models import CustomUser, Experience, Education, Skill, Language, Project

admin.site.register(CustomUser)
admin.site.register(Experience)
admin.site.register(Education)
admin.site.register(Skill)
admin.site.register(Language)
admin.site.register(Project)