from django.db import models
from demographics.models import Demographics
from video_profile.models import VideoProfile


# Create your models here.
class UserProfile(models.Model):
    demographics = models.OneToOneField(
        Demographics,
        on_delete=models.CASCADE,
    )
        
    userID            = models.CharField(max_length=50) 
    preferredLanguage = models.CharField(max_length=20)
    username          = models.CharField(max_length=20, default="")

    allFollowings = models.ManyToManyField('self', through='Relationships', symmetrical=False)
    allFriends    = models.ManyToManyField('self')

    def get_all_followings(self, relation):
        followings = self.allFollowings.filter(
            creator__relation=relation
        )
        if followings == []: return None
        else:                return [{"username":creator.username, "userID":creator.userID} 
                                        for creator in followings]

    def get_friends(self):
        allFriends = self.allFriends.all()
        if allFriends == []: return None
        else:                return [{"username":creator.username, "userID":creator.userID} 
                                        for creator in allFriends]

    # createdVideos = models.ManyToManyField(VideoProfile, related_name="created_video")
    # watchedVideos = models.ManyToManyField(VideoProfile, related_name="watched_video")


class Relationships(models.Model):
    following = 0
    blocked   = 1

    RELATION_TYPE = (
        (following, 'Following'),
        (blocked, 'Blocked'),
    )

    follower = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name="follower")
    creator  = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name="creator")
    relation = models.IntegerField(choices=RELATION_TYPE, default=following)

