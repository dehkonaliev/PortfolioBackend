from django.db import models
from django.contrib.auth.models import AbstractUser
from baseapp.models import BaseModel


class CustomUser(AbstractUser, BaseModel):
    job_title = models.CharField(max_length=200, null=True, blank=True)
    summary = models.CharField(max_length=2000, null=True, blank=True)
    address = models.CharField(max_length=300, null=True, blank=True)
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    linkedin_url = models.URLField(null=True, blank=True)
    profile_photo = models.ImageField(upload_to='avatars/', blank=True, null=True)
    profile_thumbnail = models.ImageField(upload_to='avtars_thumb/', blank=True, null=True)
    

class Experience(BaseModel):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='experiences')
    job = models.CharField(max_length=200)
    company = models.CharField(max_length=200)
    from_date = models.DateField()
    to_date = models.DateField()
    location = models.CharField(max_length=300)
    
    
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
    certification = models.FileField(upload_to='certifications/', blank=True, null=True)
    
class Project(BaseModel):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='projects')
    name = models.CharField(max_length=200)
    description = models.CharField(max_length=5000, null=True, blank=True)
    technologies = models.CharField(max_length=500, blank=True, null=True)
    cover_image = models.ImageField(upload_to='porjects/', blank=True, null=True)
    link = models.URLField(null=True, blank=True)
    
    
    
    

    