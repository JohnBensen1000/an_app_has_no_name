import sys
import json
import os
import datetime

from django.http import HttpResponse, JsonResponse
from django.apps import apps
from django.views.decorators.csrf import csrf_exempt

import methods.nsfw_filter as nsfw_filter
import methods.send_email as send_email

import firebase_admin

import methods.activity_feed as activity_feed

# default_app = firebase_admin.initialize_app()

User        = apps.get_model("models", "User")
Preferences = apps.get_model("models", "Preferences")
Profile     = apps.get_model("models", "Profile")
Blocked     = apps.get_model("models", "Blocked")
ChatMember  = apps.get_model("models", "ChatMember")
Chat        = apps.get_model("models", "Chat")
Post        = apps.get_model("models", "Post")
Following   = apps.get_model("models", "Following")

@csrf_exempt
def followings(request, uid=None):
    try:
        # Creates a new following relationship between the user and the creator. If the user has 
        # been blocking the creator, then deletes the blocking relationship. Checks if the creator 
        # is following the user. If they are, then sets the field "newFollower" to False in that
        # relationship (even if it is already False) and creates a new direct message between these
        # two users. If they are not, then newFollower is set to true in the new following 
        # relationship. Checks to see if the following relationship already exists before creating 
        # any new entries into the database. 
        if request.method == "POST":
            user        = User.objects.get(uid=uid)
            requestBody = json.loads(request.body)
            creator     = User.objects.get(uid=requestBody['uid'])
            newFollower = True

            if Following.objects.filter(follower=user, creator=creator).exists():
                return JsonResponse({'denied': 'already_following'})

            if Blocked.objects.filter(user=user, creator=creator).exists():
                Blocked.objects.filter(user=user, creator=creator).delete()

            if Following.objects.filter(follower=creator, creator=user).exists():
                newFollower           = False
                following             = Following.objects.get(follower=creator, creator=user)
                following.newFollower = False
                following.save()

                chat = Chat.objects.create(isDirectMessage=True)
                ChatMember.objects.create(isOwner=True, chat=chat, member=user)
                ChatMember.objects.create(isOwner=True, chat=chat, member=creator)

                activity_feed.add_follower(creator, user)
                
            else:
                activity_feed.add_new_follower(creator, user)

            following = Following.objects.create(
                follower    = user,
                creator     = creator,
                newFollower = newFollower, 
            )

            return JsonResponse(following.to_dict())

        # Returns a list of all creators that a user is following. Shows if each creator is a 
        # friend of the user or not. 
        if request.method == "GET":
            user           = User.objects.get(uid=uid)
            followingsList = list()
            for following in Following.objects.filter(follower=user):
                creator = following.creator
                followingsList.append({
                    "user":     creator.to_dict(),
                    "isFriend": Following.objects.filter(follower=creator, creator=user).exists()
                })

            return JsonResponse({"followings": followingsList})

        # # Returns a list of all creators that a user is following. 
        # if request.method == "GET":
        #     user           = User.objects.get(uid=uid)
        #     followingsList = list()
        #     for following in Following.objects.filter(follower=user):
        #         followingsList.append(following.creator.uid)

            # return JsonResponse({"followings": followingsList})

    except:
        print(" [ERROR]", sys.exc_info())
        return HttpResponse(status=500)

@csrf_exempt
def following(request, uid=None, uid1=None):
    try:
        # Checks to see if a user (identified by uid0) is followering another user (identified by uid1)
        if request.method == "GET":
            follower  = User.objects.get(uid=uid)
            creator   = User.objects.get(uid=uid1)

            isFollowing = Following.objects.filter(follower=follower, creator=creator).exists()
            return JsonResponse({"isFollowing": isFollowing})

        # If a user decides to not follow back a creator, then they could update the creator->user following
        # relationship to set "newFollower" to false.
        if request.method == "PUT":
            follower  = User.objects.get(uid=uid)
            creator   = User.objects.get(uid=uid1)
            following = Following.objects.get(follower=follower, creator=creator)
            following.newFollower = False
            following.save()

            return JsonResponse(following.to_dict())
            
        # Deletes a one-way following relationship. If follower is friends with the creator, then
        # deletes the direct message between the two. This includes deleting the chat data in 
        # firestore and the chat entity in the database. 
        if request.method == "DELETE":
            follower  = User.objects.get(uid=uid)
            creator   = User.objects.get(uid=uid1)
            
            following = Following.objects.get(follower=follower, creator=creator)
            following.delete()

            return JsonResponse({'deleted': True})


    except:
        print(" [ERROR]", sys.exc_info())
        return HttpResponse(status=500)