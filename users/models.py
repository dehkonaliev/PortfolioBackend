from django.db import models
from django.contrib.auth.models import AbstractUser
from baseapp.models import BaseModel
from django.utils import timezone
from datetime import timedelta
import secrets
from .validators import validate_cover_image_size, validate_certification_size


class CustomUser(AbstractUser, BaseModel):
    job_title = models.CharField(max_length=200, null=True, blank=True)
    summary = models.CharField(max_length=2000, null=True, blank=True)
    address = models.CharField(max_length=300, null=True, blank=True)
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    linkedin_url = models.URLField(null=True, blank=True)
    telegram_url = models.URLField(null=True, blank=True)
    profile_photo = models.ImageField(upload_to='avatars/', blank=True, null=True)
    profile_thumbnail = models.ImageField(upload_to='avatars_thumb/', blank=True, null=True)
    
    
def default_expiry():
    return timezone.now() + timedelta(minutes=15)

class TempUser(BaseModel):
    email = models.EmailField(max_length=100)
    code = models.IntegerField(blank=True, null=True)
    expiry_time = models.DateTimeField(default=default_expiry)


class Experience(BaseModel):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='experiences')
    job = models.CharField(max_length=200)
    company = models.CharField(max_length=200)
    activity = models.CharField(max_length=2000, blank=True, null=True)
    from_date = models.DateField()
    to_date = models.DateField()
    location = models.CharField(max_length=300, blank=True, null=True)
    
    
class Language(BaseModel):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='languages')
    language = models.CharField(max_length=30)
    level = models.CharField(max_length=20)
    issued_by = models.CharField(max_length=30)


class Skill(BaseModel):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='skills')
    name = models.CharField(max_length=50)
    level = models.IntegerField()
    
    
class Education(BaseModel):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='educations')
    field = models.CharField(max_length=100)
    edu_place = models.CharField(max_length=200)
    from_date = models.DateField()
    to_date = models.DateField()
    what_learnt = models.CharField(max_length=2000)
    certification = models.FileField(upload_to='certifications/', blank=True, null=True,
                                     validators=[validate_certification_size])
    
class Project(BaseModel):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='projects')
    name = models.CharField(max_length=200)
    description = models.CharField(max_length=5000, null=True, blank=True)
    technologies = models.CharField(max_length=500, blank=True, null=True)
    cover_image = models.ImageField(upload_to='projects/', blank=True, null=True,
                                    validators=[validate_cover_image_size])
    url = models.URLField(null=True, blank=True)

def generate_token():
    return secrets.token_urlsafe(32)
    
class MyToken(BaseModel):
    temp_user = models.ForeignKey(TempUser, on_delete=models.CASCADE, related_name='my_tokens')
    token = models.CharField(max_length=64, default=generate_token)
    
    
class JobTitle(BaseModel):
    job_title = models.CharField(max_length=200, unique=True)
    usage_counts = models.PositiveIntegerField(default=0)
    
class Technology(BaseModel):
    technology = models.CharField(max_length=200, unique=True)
    usage_counts = models.PositiveIntegerField(default=0)
    
class Field(BaseModel):
    field = models.CharField(max_length=200, unique=True)
    usage_counts = models.PositiveIntegerField(default=0)
    
class SkillUnique(BaseModel):
    skill = models.CharField(max_length=200, unique=True)
    usage_counts = models.PositiveIntegerField(default=0)
    
    