import sys

from django.shortcuts import render
from user_profile.models import UserProfile
from post_profile.models import *
from demographics.models import *
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
# Create your views here.

from graph_data.models import *

config.ENCRYPTED_CONNECTION = False
config.DATABASE_URL = 'bolt://neo4j:PulpFiction1@localhost:7687' # default


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
def record_watched(request, userID=None, postID=None):
	try:
		watchedJson = request.POST
		post = Post.objects.get(postID=postID)
		user = User.objects.get(userID=userID)

		watched = Watched.objects.create(
			user       = user,
			post       = post,
			userRating = int(watchedJson["userRating"]),
		)
		return HttpResponse("Successfully recorded that user watched a video.")

	except:
		return HttpResponse(str(sys.exc_info()[0]))
		

if __name__ == "__main__":
	pass