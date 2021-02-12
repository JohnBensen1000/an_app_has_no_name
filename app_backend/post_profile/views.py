import sys
import numpy as np
import glob

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


# cred = credentials.Certificate("../an-app-has-no-name-059c876a8538.json")
# initialize_app(cred, {'storageBucket': 'an-app-has-no-name.appspot.com'})

client = storage.Client(project="an-app-has-no-name")
bucket = client.get_bucket("an-app-has-no-name.appspot.com")

@csrf_exempt
def posts(request, userID=None):
	try:
		userProfile = UserProfile.objects.get(userID=userID)

		if request.method == "GET":
			userPosts = {
				"userPosts": [{"id":post.postID, "timeCreated":post.timeCreated} 
								for post in userProfile.created.all()]
			}
			return JsonResponse(userPosts)

		if request.method == "POST":
			imageFile = request.FILES['media']

			postDemo = Demographics.objects.create()

			postProfile = request.POST
			newPost = PostProfile.objects.create(
				demographics = postDemo,
				creator      = userProfile
			)

			# uploads post to google cloud storage
			blob = bucket.blob("%s/%s.png" % (userID, newPost.postID))
			blob.content_type = "image/png"
			blob.upload_from_file(imageFile)

			return JsonResponse({"postID": newPost.postID})

		else:
			return HttpResponse("This method is not supported by this function.")

	except:
		return HttpResponse(str(sys.exc_info()[0]))

@csrf_exempt
def recommended_posts(request, userID=None):
	try:
		user       = UserProfile.objects.get(userID=userID)
		userDemo   = np.array(user.demographics.get_list())
		linkedList = LinkedList()

		#print(" [x] UserID: %s, sumDemo: %s, demographics: %s" % (userID, str(sum(userDemo)), str(np.round(userDemo, 2)))) 
		
		for post in PostProfile.objects.exclude():
			#print("    [x] PostID: %s, creatorID: %s, demographics: %s" % (post.postID, post.creator.userID, str(post.demographics.get_list())))
			
			if not (post.watchedBy.filter(userID=userID).exists() or post.creator.userID == userID):
					postDemo = np.array(post.demographics.get_list())
					score    = np.dot(postDemo, userDemo)
					score    = score / (1 + np.abs(score))

					postNode = PostNode(post.creator.userID, post.postID, score)
					linkedList.add_node(postNode)
					#print("    [x] Score: %s" % str(score))
		
		return JsonResponse({"Posts": linkedList.get_list_of_nodes()})

	except:
		return HttpResponse(str(sys.exc_info()[0]))

@csrf_exempt
def following_posts(request, userID=None):
	try:
		user       = UserProfile.objects.get(userID=userID)
		followings = user.get_followings()

		postsList = list()
		for creator in followings:
			for post in PostProfile.objects.filter(creator=creator):
				postsList.append({"userID": creator.userID, "username": creator.username, "postID": post.postID})

		return JsonResponse({"postsList": postsList})

	except:
		print("  [x]", str(sys.exc_info()[0]))
		return HttpResponse(status=500)

@csrf_exempt
def watched(request, userID=None, postID=None):
	try:
		if request.method == "POST":
			watchedJson = request.POST
			user = UserProfile.objects.get(userID=userID)
			post = PostProfile.objects.get(postID=postID)

			update_demographics(user, post, float(watchedJson["userRating"]))

			post.watchedBy.add(user)

			return HttpResponse(status=201)

	except:
		print("  [x]", str(sys.exc_info()[0]))
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

if __name__ == "__main__":
	pass