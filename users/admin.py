from django.contrib import admin
from .models import (CustomUser, Experience, Education, Skill, Language, Project, TempUser,
    MyToken, SkillUnique, Feedback, Field, Technology, JobTitle, SocialLink
)


class SocialLinkInline(admin.TabularInline):
    model = SocialLink
    extra = 0


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    inlines = [SocialLinkInline]


admin.site.register(Experience)
admin.site.register(Education)
admin.site.register(Skill)
admin.site.register(Language)
admin.site.register(Project)
admin.site.register(TempUser)
admin.site.register(MyToken)
admin.site.register(SkillUnique)
admin.site.register(Feedback)
admin.site.register(Field)
admin.site.register(JobTitle)
admin.site.register(Technology)
admin.site.register(SocialLink)