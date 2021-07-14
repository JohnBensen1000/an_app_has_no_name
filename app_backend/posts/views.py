import sys
import json
import os
from datetime import datetime
import smtplib
import ssl

import numpy as np

from django.http import HttpResponse, JsonResponse
from django.apps import apps
from django.views.decorators.csrf import csrf_exempt

from google.cloud import storage

User        = apps.get_model("models", "User")
Preferences = apps.get_model("models", "Preferences")
Profile     = apps.get_model("models", "Profile")
Post        = apps.get_model("models", "Post")
WatchedBy   = apps.get_model("models", "WatchedBy")
Reported    = apps.get_model("models", "Reported")

client = storage.Client(project=os.getenv("CLIENT"))
bucket = client.get_bucket(os.getenv("BUCKET"))

@csrf_exempt
def watched_list(request, postID=None):
	try:
		# Creates a watchedBy entity to record that a user has watched a post. Updates both
		# the user's and post's preferences lists based on the user's feedback. If the user
		# has already watched the post, then no new entity is created.
		
		if request.method == "POST":
			watchedJson = json.loads(request.body)
			user = User.objects.get(uid=watchedJson['uid'])
			post = Post.objects.get(postID=postID)

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

			return HttpResponse(status=201)

	except:
		print(" [ERROR]", sys.exc_info())
		return HttpResponse(status=500)

@csrf_exempt
def posts(request, uid=None):
	try:
		user = User.objects.get(uid=uid)

		# Returns a list of all of a user's posts. TODO: only return private post if user is friends
		# with the creator. 
		if request.method == "GET":
			userPostsList = []
			for post in user.created.all().order_by('-timeCreated'):
				userPostsList.append(post.to_dict())	
					
			return JsonResponse({"posts": userPostsList})

		# Receives meta-data about a post and the post's image of video file. Creates a new post
		# entity and uploads the post file to google storage in the right location and with the
		# right file extension and content type. 
		if request.method == "POST":
			postID      = str(int(100 * datetime.now().timestamp()))
			newPostJson = json.loads(request.body)

			newPost = Post.objects.create(
				postID      = postID,
				preferences = Preferences.objects.create(),
				creator     = user,
				isImage	    = newPostJson["isImage"],
				isPrivate   = newPostJson["isPrivate"],
				downloadURL = newPostJson["downloadURL"]
			)

			return HttpResponse(status=201)

	except:
		print(" [ERROR]", sys.exc_info())
		return HttpResponse(status=500)

@csrf_exempt
def profile(request, uid=None):
	try:
		# Gets the profile status of a user's profile.
		if request.method == "GET":
			user = User.objects.get(uid=uid)
			return JsonResponse(user.profile.to_dict())

		# Allows a user to upload a new image/video as their profile. Saves the uploaded file
		# in google storage and updates the user's profile entity.
		elif request.method == "POST":
			profileJson = json.loads(request.body)

			user = User.objects.get(uid=uid)
			user.profile.exists      = True
			user.profile.isImage     = profileJson["isImage"]
			user.profile.downloadURL = profileJson['downloadURL']
			user.profile.save()

			return HttpResponse(status=201)

	except:
		print(" [ERROR]", sys.exc_info())
		return HttpResponse(status=500)

@csrf_exempt
def post(request, uid=None, postID=None):
	try:
		post = Post.objects.get(postID=postID)
		if post.creator.uid != uid:
			return HttpResponse(status=401)

		if request.method == "POST":
			post.isPrivate = json.loads(request.body)["isPrivate"]
			post.save()

			return HttpResponse(status=200)

		if request.method == "DELETE":
			post.delete_post()
			
			return HttpResponse(status=200)

	except:
		print(" [ERROR]", sys.exc_info())
		return HttpResponse(status=500)


@csrf_exempt
def reports(request, uid=None, postID=None):
	try:
		# If the user reports an indivudal post, sends an email to the administrator
		# with the post's details. The administrator can then decide whether to delete
		# the post or not. Also created a new report entity that contains the user that
		# reported the post and the post itself. 

		if request.method == "POST":
			post = Post.objects.get(postID=postID)
			user = User.objects.get(uid=uid)

			Reported.objects.create(user=user, post=post)

			send_reported_content_email(post)

			return HttpResponse(status=201)
	except:
		print(" [ERROR]", sys.exc_info())
		return HttpResponse(status=500)

def send_reported_content_email(post):
	port    = 465 
	context = ssl.create_default_context()

	with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
		server.login("entropy.developer1@gmail.com", "CominG1$is@Winter6*9sNow11")
		server.sendmail(
			"entropy.developer1@gmail.com", 
			"entropy.developer1@gmail.com", 
			"""
				%s

				Post ID: %s
			 	Download URL: %s
				User: %s
			""" % (os.getenv("ENVIRONMENT"), post.postID, post.downloadURL, post.creator.uid)
		)
