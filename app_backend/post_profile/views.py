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
def update_posts(request, userID=None):
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
			return HttpResponse("Successfully posted new post!")

		else:
			return HttpResponse("This method is not supported by this function.")

	except:
		return HttpResponse(str(sys.exc_info()[0]))

@csrf_exempt
def get_recommended_posts(request, userID=None):
	try:
		user       = UserProfile.objects.get(userID=userID)
		userDemo   = np.array(user.demographics.get_list())
		linkedList = LinkedList()

		#print(" [x] UserID: %s, sumDemo: %s, demographics: %s" % (userID, str(sum(userDemo)), str(np.round(userDemo, 2)))) 
		
		for post in PostProfile.objects.all():
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
def record_watched(request, userID=None, postID=None):
	try:
		watchedJson = request.POST
		user = UserProfile.objects.get(userID=userID)
		post = PostProfile.objects.get(postID=postID)

		post.watchedBy.add(user)

		return HttpResponse("Successfully recorded that user watched a video.")

	except:
		return HttpResponse(str(sys.exc_info()[0]))
		
		
if __name__ == "__main__":
	pass