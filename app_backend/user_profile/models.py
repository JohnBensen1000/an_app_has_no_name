import json

from django.db import models
from demographics.models import Demographics


class AccountInfo(models.Model):
    email = models.CharField(max_length=50) 
    phone = models.CharField(max_length=15) 
    preferredLanguage = models.CharField(max_length=20)
    profileType       = models.CharField(max_length=10, default="none")


class UserProfile(models.Model):
    userID   = models.CharField(max_length=50) 
    username = models.CharField(max_length=20, default="")

    deviceToken = models.TextField(default="")
    firebaseSub = models.TextField(default="")    # "sub" field of id token

    accountInfo  = models.OneToOneField(AccountInfo,  on_delete=models.CASCADE, default=None)
    demographics = models.OneToOneField(Demographics, on_delete=models.CASCADE)

    allRelationships = models.ManyToManyField(
        'self', 
        through='Relationships', 
        symmetrical=False
    )
    # allFriends = models.ManyToManyField('self')


    def get_user_info_json(self):
        userJson = {
            "userID":            self.userID,
            "username":          self.username,
            "preferredLanguage": self.preferredLanguage,
            "email":             self.accountInfo.email,
            "phone":             self.accountInfo.phone,
        }
        return json.dumps(userJson)

    def delete_user(self):
        if self.accountInfo:
            self.accountInfo.delete()
        if self.demographics:
            self.demographics.delete()

        return super(self.__class__, self).delete()


    def get_followings(self):
        allFollowings = [relation.creator for relation in 
                            self.followings.filter(relation=Relationships.following)]
        return allFollowings

    def get_followers(self):
        allFollowers = [relation.follower for relation in 
            self.followers.filter(relation=Relationships.following)]
        allFollowings = [relation.creator for relation in 
            self.followings.filter(relation=Relationships.following)]

        followers = [user for user in allFollowers if user not in allFollowings]

        return self.__parse_user_list(followers)

    def get_friends(self):
        allFollowers = [relation.follower for relation in 
            self.followers.filter(relation=Relationships.following)]
        allFollowings = [relation.creator for relation in 
            self.followings.filter(relation=Relationships.following)]

        allFriends = [user for user in allFollowers if user in allFollowings]

        return self.__parse_user_list(allFriends)


    def __parse_user_list(self, userList):
        if userList == []: 
            return []
        return [{"username":user.username, "userID":user.userID} 
            for user in userList]


class Relationships(models.Model):
    following = 0
    blocked   = 1
    
    RELATION_TYPE = (
        (following, 'Following'),
        (blocked, 'Blocked'),
    )

    follower    = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name="followings")
    creator     = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name="followers")
    relation    = models.IntegerField(choices=RELATION_TYPE, default=following)
    newFollower = models.BooleanField(default=True)


