from django.db import models
from demographics.models import Demographics
from user_profile import UserProfile

# Create your models here.
class VideoProfile(models.Model):
	private = models.BooleanField(default=False)

	demographics = models.OneToOneField(
		Demographics,
		on_delete=models.CASCADE,
	)

	creator = models.ForeignKey(
		UserProfile, 
		on_delete=models.CASCADE, 
		backref='postedVideos'
	)

    watchedBy = models.ManyToManyField(
    	UserProfile, 
    	on_delete=models.CASCADE, 
    )

