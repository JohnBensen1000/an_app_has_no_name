from datetime import datetime    

from django.db import models
from demographics.models import Demographics
from user_profile.models import UserProfile

# Create your models here.
class VideoProfile(models.Model):
	videoID = models.AutoField(primary_key=True)
	private = models.BooleanField(default=False)
	timeCreated = models.DateTimeField(default=datetime.now) 

	demographics = models.OneToOneField(
		Demographics,
		on_delete=models.CASCADE,
	)

	creator = models.ForeignKey(
		UserProfile, 
		on_delete=models.CASCADE, 
		related_name="created"
	)

	watchedBy = models.ManyToManyField(
		UserProfile, 
		related_name="watched"
	)