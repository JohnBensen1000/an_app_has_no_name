from datetime import datetime    

from django.db import models
from user_profile.models import UserProfile
from demographics.models import Demographics

# Create your models here.
class PostProfile(models.Model):
	postID  = models.AutoField(primary_key=True)
	private = models.BooleanField(default=False)
	timeCreated = models.DateTimeField(default=datetime.now) 

	demographics = models.OneToOneField(Demographics, on_delete=models.CASCADE)
	creator = models.ForeignKey(UserProfile, 
								on_delete=models.CASCADE, 
								related_name="created")

	watchedBy = models.ManyToManyField(
		UserProfile,
		through='Watched',
        symmetrical=False,
	)

class Watched(models.Model):
	wantsLess   = -1
	inDifferent = 0
	wantsMore   = 1

	WATCHED_TYPE = (
        (wantsLess, 'Wants_less_of_same_content'),
        (inDifferent, 'Indifferent_to_post'),
        (wantsMore, 'Wants_more_of_same_content'),
    )

	user        = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name="watched")
	post        = models.ForeignKey(PostProfile, on_delete=models.CASCADE, related_name="watched_by")
	timeWatched = models.DateTimeField(default=datetime.now) 
	userRating  = models.IntegerField(choices=WATCHED_TYPE, default=inDifferent)
