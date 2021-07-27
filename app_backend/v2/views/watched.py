import sys
import json
import os

import numpy as np

from django.http import HttpResponse, JsonResponse
from django.apps import apps
from django.views.decorators.csrf import csrf_exempt

from google.cloud import storage, vision

User        = apps.get_model("models", "User")
Preferences = apps.get_model("models", "Preferences")
Profile     = apps.get_model("models", "Profile")
Post        = apps.get_model("models", "Post")
WatchedBy   = apps.get_model("models", "WatchedBy")
Reported    = apps.get_model("models", "Reported")

client = storage.Client(project=os.getenv("CLIENT"))
bucket = client.get_bucket(os.getenv("BUCKET"))

visionClient = vision.ImageAnnotatorClient()

@csrf_exempt
def watched(request, postID=None):
    try:
        # Creates a watchedBy entity to record that a user has watched a post. Updates both
        # the user's and post's preferences lists based on the user's feedback. If the user
        # has already watched the post, then no new entity is created.
        
        if request.method == "POST":
            watchedJson = json.loads(request.body)
            user        = User.objects.get(uid=watchedJson['uid'])
            post        = Post.objects.get(postID=postID)

            if WatchedBy.objects.filter(user=user, post=post).exists():
                return HttpResponse(status=200)

            userPref = np.array(user.preferences.list)
            postPref = np.array(post.preferences.list)
            
            stepSize  = .01
            userPref += stepSize * watchedJson['userRating'] * postPref
            postPref += stepSize * watchedJson['userRating'] * userPref

            for i, pref in enumerate(userPref):
                if pref < 0.0: userPref[i] = 0
                if pref > 1.0: userPref[i] = 1 
            for i, pref in enumerate(postPref):
                if pref < 0.0: postPref[i] = 0
                if pref > 1.0: postPref[i] = 1 
            
            user.preferences.list = userPref
            post.preferences.list = postPref

            WatchedBy.objects.create(user=user, post=post)

            return JsonResponse({'postID': postID, 'uid': user.uid})

    except:
        print(" [ERROR]", sys.exc_info())
        return HttpResponse(status=500)