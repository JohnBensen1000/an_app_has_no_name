import sys
import json
import random

from django.http import HttpResponse, JsonResponse
from django.apps import apps

from google.cloud import firestore

db = firestore.Client()

User          = apps.get_model("models", "User")
Preferences   = apps.get_model("models", "Preferences")
Profile       = apps.get_model("models", "Profile")
Relationships = apps.get_model("models", "Relationships")
ChatMember    = apps.get_model("models", "ChatMember")
Chat          = apps.get_model("models", "Chat")

def create_new_direct_message(user1, user2):
    chat = Chat.objects.create(
        isDirectMessage=True
    )
    
    ChatMember.objects.create(
        isOwner = True,
        chat    = chat,
        member  = user1
    )
    ChatMember.objects.create(
        isOwner = True,
        chat    = chat,
        member  = user2
    )


def followings(request, uid=None):
    try:
        user = User.objects.get(uid=uid)

        # Returns a list of all creators that a user is following. Shows if each creator is a 
        # friend of the user or not. 
        if request.method == "GET":
            followingsList = list()
            for following in user.followings.filter(relation=Relationships.following):
                creator = following.creator
                followingsList.append({
                    "uid":      creator.uid,
                    "userID":   creator.userID,
                    "username": creator.username,
                    "isFriend": Relationships.objects.filter(follower=creator, creator=user).exists()
                })

            return JsonResponse({"followings": followingsList})

        # Creates a relationship entity that stores the fact that a user is following a creator. The 
        # creator is identified by 'uid' given in the request body. 'newFollower' is a field in 
        # Relationship that keeps track of whether or not to notify a creator that a new user started
        # following them. This will only be set to True if the creator is not already following that 
        # new user. 
        if request.method == "POST":
            requestBody = json.loads(request.body)
            creator     = User.objects.get(uid=requestBody['uid'])
            isNewFriend = Relationships.objects.filter(follower=creator, creator=user).exists()

            Relationships.objects.create(
                follower    = user,
                creator     = creator,
                newFollower = not isNewFriend, 
            )

            if isNewFriend:
                create_new_direct_message(user, creator)

            return HttpResponse(status=201)	

    except:
        print(" [ERROR]", sys.exc_info())
        return HttpResponse(status=500)

def following(request, uid0=None, uid1=None):
    try:
        follower  = User.objects.get(uid=uid0)
        creator   = User.objects.get(uid=uid1)

        # Checks to see if a user (identified by uid0) is followering another user (identified by uid1)
        if request.method == "GET":
            isFollowing = Relationships.objects.filter(follower=follower, creator=creator).exists()
            return JsonResponse({"isFollowing": isFollowing})

        # Allows a user to follow back or not follow back a new follower. Either way, the user's new
        # follower will no longer be labeled as a new follower. Returns a 201 status code if the user
        # decides to follow back, returns 200 otherwise. 
        if request.method == "POST":
            following             = Relationships.objects.get(follower=follower, creator=creator)
            following.newFollower = False
            following.save()

            requestBody = json.loads(request.body)

            if requestBody['followBack']:
                Relationships.objects.create(
                    follower    = creator,
                    creator     = follower,
                    newFollower = False, 
                )
                create_new_direct_message(follower, creator)

                return HttpResponse(status=201)
            else:
                return HttpResponse(status=200)

        # Deletes a one-way following relationship. 
        if request.method == "DELETE":
            following = Relationships.objects.get(follower=follower, creator=creator)
            following.delete()
            return HttpResponse(status=200)

    except:
        print(" [ERROR]", sys.exc_info())
        return HttpResponse(status=500)

def followers(request, uid=None):
    try:
        # Returns a list of all of a user's (identified by uid) followers.
        if request.method == "GET":
            user         = User.objects.get(uid=uid)
            followerList = list() 
            for relationship in Relationships.objects.filter(creator=user):
                followerList.append(relationship.follower.to_dict())

            return JsonResponse({'followerList': followerList})

    except:
        print(" [ERROR]", sys.exc_info())
        return HttpResponse(status=500)

def new_followers(request, uid=None):
    try:
        # Returns a list of all of a user's (identified by uid) new followers.
        if request.method == "GET":
            user         = User.objects.get(uid=uid)
            followerList = list() 
            for relationship in Relationships.objects.filter(creator=user, newFollower=True):
                followerList.append(relationship.follower.to_dict())

            return JsonResponse({'followerList': followerList})
    except:
        print(" [ERROR]", sys.exc_info())
        return HttpResponse(status=500)

def friends(request, uid=None):
    try:
        # Returns a list of all a user's friends. A 'friend' is defined as another user that
        # both follows and is followed by a user. 
        if request.method == "GET":
            user        = User.objects.get(uid=uid)
            friendsList = list() 

            for relationship in Relationships.objects.filter(creator=user):
                follower = relationship.follower
                if Relationships.objects.filter(creator=follower, follower=user):
                    friendsList.append(follower.to_dict())

            return JsonResponse({'friendsList': friendsList})

    except:
        print(" [ERROR]", sys.exc_info())
        return HttpResponse(status=500)
