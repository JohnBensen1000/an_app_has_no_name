import sys
import numpy as np

from django.shortcuts import render
from user_profile.models import UserProfile
from post_profile.models import *
from demographics.models import *
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .linked_list import *

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
			postDemo = Demographics.objects.create()

			postProfile = request.POST
			newPost = PostProfile.objects.create(
				demographics = postDemo,
				creator      = userProfile
			)
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
def watched(request, userID=None, postID=None):
	try:
		watchedJson = request.POST
		user = UserProfile.objects.get(userID=userID)
		post = PostProfile.objects.get(postID=postID)

		update_demographics(user, post, float(watchedJson["userRating"]))

		post.watchedBy.add(user)

		return HttpResponse("Successfully recorded that user watched a video.")

	except:
		return HttpResponse(str(sys.exc_info()[0]))

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

# def following_posts(request, userID=None):
# 	if request.method == "GET":
# 		user = UserProfile.objects.get(userID=userID)

# 		for 

if __name__ == "__main__":
	pass