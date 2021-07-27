import sys
import json

import numpy as np

from firebase_admin import auth

from django.http import HttpResponse, JsonResponse
from django.apps import apps
from django.views.decorators.csrf import csrf_exempt

import methods.send_email as send_email

User          = apps.get_model("models", "User")
Preferences   = apps.get_model("models", "Preferences")
Profile       = apps.get_model("models", "Profile")
Post          = apps.get_model("models", "Post")
Following     = apps.get_model("models", "Following")
Blocked       = apps.get_model("models", "Blocked")
WatchedBy     = apps.get_model("models", "WatchedBy")
Reported      = apps.get_model("models", "Reported")

@csrf_exempt
def report_post(request, uid=None):
	try:
		# If the user reports an indivudal post, sends an email to the administrator
		# with the post's details. The administrator can then decide whether to delete
		# the post or not. Also created a new report entity that contains the user that
		# reported the post and the post itself. 

		if request.method == "POST":
			requestBody = json.loads(request.body)

			post = Post.objects.get(postID=requestBody["postID"])
			user = User.objects.get(uid=uid)

			Reported.objects.create(user=user, post=post)

			send_email.send_email({
                "postID": post.postID,
                "download url": post.downloadURL,
                'user': str(post.creator.to_dict())
            })

			return JsonResponse({'post': post.postID, 'uid': user.uid})

	except:
		print(" [ERROR]", sys.exc_info())
		return HttpResponse(status=500)

@csrf_exempt
def report_comment(request, uid=None, postID=None):
    try:
        # Allows user to report individual comment. 
        if request.method == "POST":
            emailDict           = json.loads(request.body)
            emailDict['postID'] = postID

            send_email.send_email(emailDict)

            return JsonResponse({'post': postID, 'uid': uid})

    except:
        print(" [ERROR]", sys.exc_info())
        return HttpResponse(status=500)

@csrf_exempt
def report_profile(request, uid=None):
    try:
        if request.method == "POST":
            requestBody  = json.loads(request.body)
            reportedUser = User.objects.get(uid=requestBody["uid"])
            profile      = reportedUser.profile

            send_email.send_email({
                "uid": reportedUser.uid,
                "download url": profile.downloadURL,
            })

            return JsonResponse({'uid': uid})

    except:
        print(" [ERROR]", sys.exc_info())
        return HttpResponse(status=500)