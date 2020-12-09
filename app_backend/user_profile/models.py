from django.db import models
from demographics.models import Demographics


class AccountInfo(models.Model):
    email = models.CharField(max_length=50) 
    phone = models.CharField(max_length=10) 


class UserProfile(models.Model):
    userID   = models.CharField(max_length=50) 
    username = models.CharField(max_length=20, default="")
    preferredLanguage = models.CharField(max_length=20)

    demographics = models.OneToOneField(Demographics, on_delete=models.CASCADE)
    accountInfo  = models.OneToOneField(AccountInfo,  on_delete=models.CASCADE, default=None)
        
    allRelationships = models.ManyToManyField(
        'self', 
        through='Relationships', 
        symmetrical=False
    )
    allFriends = models.ManyToManyField('self')


    def get_followings(self):
        allFollowings = [relation.creator for relation in 
                            self.followers.filter(relation=Relationships.following)]
        return self.__return_user_list(allFollowings)


    def get_followers(self):
        allFollowers = [relation.follower for relation in 
                            self.creators.filter(relation=Relationships.following)]
        return self.__return_user_list(allFollowers)


    def get_friends(self):
        allFriends = self.allFriends.all()
        return self.__return_user_list(allFriends)


    def __return_user_list(self, userList):
        if userList == []: 
            return None
        return [{"username":user.username, "userID":user.userID} 
            for user in userList]


class Relationships(models.Model):
    following = 0
    blocked   = 1

    RELATION_TYPE = (
        (following, 'Following'),
        (blocked, 'Blocked'),
    )

    follower = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name="followers")
    creator  = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name="creators")
    relation = models.IntegerField(choices=RELATION_TYPE, default=following)


