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
def blocked(request, uid=None):
    try:
        # Creates a blocked relationship between two users. Deletes the following relationship
        # and direct message between the two users if they exist.
        if request.method == "POST":
            requestBody = json.loads(request.body)
            user        = User.objects.get(uid=uid)
            creator     = User.objects.get(uid=requestBody['uid'])  

            if Following.objects.filter(follower=user, creator=creator).exists():
                following = Following.objects.get(follower=user, creator=creator)
                following.delete()

            Blocked.objects.create(
                user    = user,
                creator = creator,
            )

            return JsonResponse(creator.to_dict())

        # Returns a list of all creators that the user is blocking.
        if request.method == "GET":
            user        = User.objects.get(uid=uid)
            blockedList = [blocked.creator.to_dict() for blocked in Blocked.objects.filter(user=user)]

            return JsonResponse({"blocked": blockedList})

    except:
        print(" [ERROR]", sys.exc_info())
        return HttpResponse(status=500)     

@csrf_exempt
def blocked_user(request, uid=None, uid1=None):
    try:
        # Deletes a blocked relationship between two users.
        if request.method == "DELETE":
            user        = User.objects.get(uid=uid)
            creator     = User.objects.get(uid=uid1)

            Blocked.objects.filter(user=user, creator=creator).delete()

            return JsonResponse({'deleted': True})

    except:
        print(" [ERROR]", sys.exc_info())
        return HttpResponse(status=500)   