import sys
import json
import datetime

from django.http import HttpResponse, JsonResponse
from django.apps import apps
from django.views.decorators.csrf import csrf_exempt

import methods.nsfw_filter as nsfw_filter
import methods.send_email as send_email

User        = apps.get_model("models", "User")
Preferences = apps.get_model("models", "Preferences")
Profile     = apps.get_model("models", "Profile")
Blocked     = apps.get_model("models", "Blocked")
ChatMember  = apps.get_model("models", "ChatMember")
Chat        = apps.get_model("models", "Chat")
Post        = apps.get_model("models", "Post")

@csrf_exempt
def posts(request, uid=None):
    try:
        # Receives meta-data about a post and the post's image or video file. Uses google vision to
        # determine if the post is NSFW or not. If it is, returns a Json object informing the client
        # that the post has been flagged due to being NSFW. Otherwise, creates a new post entity and 
        # uploads the post file to google storage in the right location and with the right file 
        # extension and content type. 
        if request.method == "POST":
            user        = User.objects.get(uid=uid)
            postID      = str(int(100 * datetime.datetime.now().timestamp()))
            newPostJson = json.loads(request.body)

            post = Post.objects.create(
                postID      = postID,
                preferences = Preferences.objects.create(),
                creator     = user,
                isImage	    = newPostJson["isImage"],
                isPrivate   = newPostJson["isPrivate"],
                downloadURL = newPostJson["downloadURL"],
                caption     = newPostJson["caption"] if "caption" in newPostJson else "",
            )

            if not nsfw_filter.check_if_post_is_safe(newPostJson['downloadURL']):
                post.isFlagged = True
                post.save()
                
                send_email.send_email({
                    'post id': post.postID,
                    'download url': post.downloadURL,
                    'user': post.creator.uid,
                })

                return JsonResponse({"denied": "NSFW"})

            else:
                return JsonResponse(post.to_dict())

        # Returns a list of all of a user's posts. Only returns posts that aren't flagged. 
        if request.method == "GET":
            user          = User.objects.get(uid=uid)
            userPostsList = []
            for post in user.created.all().order_by('-timeCreated'):
                if not post.isFlagged:
                    userPostsList.append(post.to_dict())	
                    
            return JsonResponse({"posts": userPostsList})
            
    except:
        print(" [ERROR]", sys.exc_info())
        return HttpResponse(status=500)

@csrf_exempt
def profile(request, uid=None):
    try:
        # Allows a user to upload a new image/video as their profile. Uses google vision to check
        # if the profile image/video is safe. If it is, then saves the picture/video in google storage
        # and updates the user's profile entity. If it isn't, then flags the profile and sends
        # an email to the development team. 
        if request.method == "POST":
            profileJson = json.loads(request.body)

            user = User.objects.get(uid=uid)
            user.profile.exists      = True
            user.profile.isImage     = profileJson["isImage"]
            user.profile.downloadURL = profileJson['downloadURL']
            user.profile.save()

            if not nsfw_filter.check_if_post_is_safe(profileJson['downloadURL']):
                user.profile.isFlagged = True
                user.profile.save()

                send_email.send_email({
                    'profile pk': user.profile.pk,
                    'user uid': user.uid,
                    'download url': user.profile.downloadURL,
                })

                return JsonResponse({"denied": "NSFW"})

            else:
                return JsonResponse(user.profile.to_dict())

        # Gets the profile status of a user's profile.
        if request.method == "GET":
            user = User.objects.get(uid=uid)
            return JsonResponse(user.profile.to_dict())

    except:
        print(" [ERROR]", sys.exc_info())
        return HttpResponse(status=500)

@csrf_exempt
def post(request, uid=None, postID=None):
    try:
        # Simply returns the post dict for the post identified by postID.
        if request.method == "GET":
            post = Post.objects.get(postID=postID)
            return JsonResponse(post.to_dict())

        # Allows a user to delete one of their posts.
        if request.method == "DELETE":
            post = Post.objects.get(postID=postID)
            post.delete_post()
            
            return JsonResponse({'deleted': True})

    except:
        print(" [ERROR]", sys.exc_info())
        return HttpResponse(status=500)