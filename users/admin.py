from django.contrib import admin
from .models import (CustomUser, Experience, Education, Skill, Language, Project, TempUser,
    MyToken, SkillUnique
)

admin.site.register(CustomUser)
admin.site.register(Experience)
admin.site.register(Education)
admin.site.register(Skill)
admin.site.register(Language)
admin.site.register(Project)
admin.site.register(TempUser)
admin.site.register(MyToken)
admin.site.register(SkillUnique)