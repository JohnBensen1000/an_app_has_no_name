import sys
import json
import os
from datetime import datetime

import numpy as np

from django.http import HttpResponse, JsonResponse
from django.apps import apps
from django.views.decorators.csrf import csrf_exempt

from google.cloud import storage

User        = apps.get_model("models", "User")
Preferences = apps.get_model("models", "Preferences")
Profile     = apps.get_model("models", "Profile")
Post        = apps.get_model("models", "Post")

client = storage.Client(project="an-app-has-no-name")
bucket = client.get_bucket("an-app-has-no-name.appspot.com")

@csrf_exempt
def watched_list(request, postID=None):
	try:
		# Creates a watchedBy entity to record that a user has watched a post. Updates both
		# the user's and post's preferences lists based on the user's feedback. 
		if request.method == "POST":
			watchedJson = json.loads(request.body)
			user = User.objects.get(uid=watchedJson['uid'])
			post = Post.objects.get(postID=postID)

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

			post.watchedBy.add(user)

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
			newPostJson = json.loads(request.POST['json'])
			postID      = str(int(100 * datetime.now().timestamp()))
			downloadURL = 'https://storage.googleapis.com/an-app-has-no-name.appspot.com/'
			directory   = os.environ["STORAGE_DIR"]

			if newPostJson['isImage']:
				postFile          = "%s/%s/%s.png" % (directory, uid, postID)		
				blob              = bucket.blob(postFile)
				blob.content_type = "image/png"
			else:
				postFile          = "%s/%s/%s.mp4" % (directory, uid, postID)		
				blob              = bucket.blob(postFile)
				blob.content_type = "video/mp4"

			downloadURL += postFile
			blob.upload_from_file(request.FILES['media'])
			blob.make_public()

			Post.objects.create(
				postID      = postID,
				preferences = Preferences.objects.create(),
				creator     = user,
				isImage	    = newPostJson["isImage"],
				isPrivate   = newPostJson["isPrivate"],
				downloadURL = downloadURL
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
			profileJson = json.loads(request.POST['json'])
			downloadURL = 'https://storage.googleapis.com/an-app-has-no-name.appspot.com/'
			directory   = os.environ["STORAGE_DIR"]

			if profileJson['isImage']:
				postFile          = "%s/%s/profile.png" % (directory, uid)		
				blob              = bucket.blob(postFile)
				blob.content_type = "image/png"
			else:
				postFile          = "%s/%s/profile.mp4" % (directory, uid)		
				blob              = bucket.blob(postFile)
				blob.content_type = "video/mp4"

			downloadURL += postFile

			blob.upload_from_file(request.FILES['media'])
			blob.make_public()
			blob.cache_control = 'max-age=0'
			blob.patch()

			user = User.objects.get(uid=uid)
			user.profile.exists      = True
			user.profile.isImage     = profileJson["isImage"]
			user.profile.downloadURL = downloadURL
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

