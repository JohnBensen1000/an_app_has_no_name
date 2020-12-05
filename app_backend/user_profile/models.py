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

    allRelationships = models.ManyToManyField(
        'self', 
        through='Relationships', 
        on_delete=models.CASCADE, 
        symmetrical=False
    )
    allFriends = models.ManyToManyField('self')

    def get_all_followings(self):
        followings = self.allRelationships.filter(
            creator__relation=Relationships.following
        )
        if followings == []: 
            return None
        return [{"username":creator.username, "userID":creator.userID} 
            for creator in followings]

    def get_friends(self):
        allFriends = self.allFriends.all()
        if allFriends == []: 
            return None
        return [{"username":creator.username, "userID":creator.userID} 
            for creator in allFriends]


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


