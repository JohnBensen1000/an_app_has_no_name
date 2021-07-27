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
def followers(request, uid=None):
    try:
        # Returns a list of all of a user's (identified by uid) followers.
        if request.method == "GET":
            user         = User.objects.get(uid=uid)
            followerList = list() 
            for relationship in Following.objects.filter(creator=user):
                followerList.append(relationship.follower.to_dict())

            return JsonResponse({'followers': followerList})

    except:
        print(" [ERROR]", sys.exc_info())
        return HttpResponse(status=500)

@csrf_exempt
def new_followers(request, uid=None):
    try:
        # Returns a list of all of a user's (identified by uid) new followers.
        if request.method == "GET":
            user         = User.objects.get(uid=uid)
            followerList = list() 
            for relationship in Following.objects.filter(creator=user, newFollower=True):
                followerList.append(relationship.follower.to_dict())

            return JsonResponse({'followers': followerList})
    except:
        print(" [ERROR]", sys.exc_info())
        return HttpResponse(status=500)