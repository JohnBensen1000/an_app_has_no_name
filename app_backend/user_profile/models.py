from django.db import models
from demographics.models import Demographics


# Create your models here.
class UserProfile(models.Model):
    demographics = models.OneToOneField(
        Demographics,
        on_delete=models.CASCADE,
    )
        
    userID            = models.CharField(max_length=50) 
    preferredLanguage = models.CharField(max_length=20)
    username          = models.CharField(max_length=20, default="")
