from datetime import datetime    

from django.db import models
from user_profile.models import UserProfile

# Create your models here.
class PostProfile(models.Model):
	postID  = models.AutoField(primary_key=True)
	private = models.BooleanField(default=False)
	timeCreated = models.DateTimeField(default=datetime.now) 

	creator = models.ForeignKey(
		UserProfile, 
		on_delete=models.CASCADE, 
		related_name="created"
	)
