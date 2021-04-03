import sys
import numpy as np

from user_profile.models import UserProfile
from post_profile.models import *
from demographics.models import *
from .linked_list import *

from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

from firebase_admin import credentials, initialize_app, storage
from google.cloud import storage
from google.cloud.storage import Blob

client = storage.Client(project="an-app-has-no-name")
bucket = client.get_bucket("an-app-has-no-name.appspot.com")

@csrf_exempt
def posts(request, userID=None):
	try:
		userProfile = UserProfile.objects.get(userID=userID)

		# Returns a list of all of a user's non-private posts.
		if request.method == "GET":
			userPostsList = []
			for post in userProfile.created.all():
				if post.private == False:
					userPostsList.append({
						"userID": userProfile.userID, 
						"username": userProfile.username, 
						"postID": post.postID, 
						"isImage": post.isImage,
					})	
					
			return JsonResponse({"userPosts": userPostsList})

		# Receives meta-data about a post and the post's image of video file. Creates a new post
		# entity and uploads the post file to google storage in the right location and with the
		# right file extension and content type. 
		if request.method == "POST":
			postDemo = Demographics.objects.create()

			newPost = PostProfile.objects.create(
				demographics = postDemo,
				creator      = userProfile,
				isImage	     = request.POST["contentType"] == 'image',
			)
			
			if request.POST["contentType"] == 'image':
				blob = bucket.blob("%s/%s.png" % (userID, postID))
				blob.content_type = "image/png"
			else:
				blob = bucket.blob("%s/%s.mp4" % (userID, postID))
				blob.content_type = "video/mp4"
			blob.upload_from_file(request.FILES['media'])

			return HttpResponse(status=201)

	except:
		print(" [ERROR]", sys.exc_info())
		return HttpResponse(status=500)

@csrf_exempt
def recommendations(request, userID=None):
	try:
		# Returns a list of recommended posts for the user. TODO: Document how the algorithm works. 
		if method.request == "GET":
			user       = UserProfile.objects.get(userID=userID)
			userDemo   = np.array(user.demographics.get_list())
			linkedList = LinkedList()
			
			for post in PostProfile.objects.exclude():
				if not (post.watchedBy.filter(userID=userID).exists() or post.creator.userID == userID):
						postDemo = np.array(post.demographics.get_list())
						score    = np.dot(postDemo, userDemo)
						score    = score / (1 + np.abs(score))

						postNode = PostNode(post.creator.userID, post.postID, score)
						linkedList.add_node(postNode)
			
			return JsonResponse({"Posts": linkedList.get_list_of_nodes()})

	except:
		print(" [ERROR]", sys.exc_info())
		return HttpResponse(status=500)

@csrf_exempt
def following(request, userID=None):
	try:
		# Returns a list of all post entities from every creator that the user is following that 
		# the user has not already watched. 
		if request.method == "GET":
			user       = UserProfile.objects.get(userID=userID)
			followings = user.get_followings()

			postsList = list()
			for creator in followings:
				for post in PostProfile.objects.filter(creator=creator):
					if user not in post.watchedBy.all():
						postsList.append({
							"userID": creator.userID, 
							"username": creator.username, 
							"postID": post.postID, 
							"isImage": post.isImage,
						})

			return JsonResponse({"postsList": postsList})

	except:
		print(" [ERROR]", sys.exc_info())
		return HttpResponse(status=500)

@csrf_exempt
def watched(request, userID=None, postID=None):
	try:
		# Creates a watchedBy entity to record that a user has watched a post. Also saves the 
		# feedback for the post from the user (whether or not the user liked the post).
		if request.method == "POST":
			watchedJson = request.POST
			user = UserProfile.objects.get(userID=userID)
			post = PostProfile.objects.get(postID=postID)

			update_demographics(user, post, float(watchedJson["userRating"]))

			post.watchedBy.add(user)

			return HttpResponse(status=201)

	except:
		print(" [ERROR]", sys.exc_info())
		return HttpResponse(status=500)

def update_demographics(user, post, userRating):
	stepSize = .01
	
	userDemo = np.array(user.demographics.get_list())
	postDemo = np.array(post.demographics.get_list())
	
	userDemo += stepSize * userRating * postDemo
	for i, demo in enumerate(userDemo):
		if demo < 0.0: userDemo[i] = 0
		if demo > 1.0: userDemo[i] = 1 
		print(demo, userDemo[i], demo < 0.0)

	postDemo += stepSize * userRating * userDemo
	
	user.demographics.set_list(userDemo)
	post.demographics.set_list(postDemo)
