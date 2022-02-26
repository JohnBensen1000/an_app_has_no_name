import sys

import numpy as np

from firebase_admin import auth

from django.http import HttpResponse, JsonResponse
from django.apps import apps
from django.db.models import Q

import methods.linked_list as linked_list

User          = apps.get_model("models", "User")
Preferences   = apps.get_model("models", "Preferences")
Profile       = apps.get_model("models", "Profile")
Post          = apps.get_model("models", "Post")
Following     = apps.get_model("models", "Following")
Blocked       = apps.get_model("models", "Blocked")
WatchedBy     = apps.get_model("models", "WatchedBy")
Reported      = apps.get_model("models", "Reported")

def recommendations_feed(request):
	try:
		# Returns a list of recommended posts for the user. At first, create a list of all posts that 
		# the user has not watched yet. This list of posts is ordered based on the dot product between 
		# the post's preference list and the user's preference list. If there is still space in the post 
		# list, fills in the rest of the list with posts that theuser did already watch (these posts 
		# are orderd based on when they were created). The list of post does not include posts from 
		# creators that the user isfollowing or is blocking. The list also does not include posts that
		# the user has created or has reported.

		if request.method == "GET":
			listSize   = 32
			user       = User.objects.get(uid=request.GET['uid'])
			userPref   = np.array(user.preferences.list)
			linkedList = linked_list.LinkedList(listSize)

			watchedList  = [watchedBy.post.postID for watchedBy in WatchedBy.objects.select_related("post").filter(user=user)]
			allowedPosts = Post.objects.select_related("preferences") \
				.exclude(creator=user) \
				.exclude(creator__blocked_by__user=user) \
				.exclude(reported_by__user=user) \
				.exclude(creator__followers__follower=user)
		 
			notWatchedPosts = allowedPosts.exclude(postID__in=watchedList)
			watchedPosts    = allowedPosts.filter(postID__in=watchedList)

			for post in notWatchedPosts.order_by('timeCreated').reverse()[:listSize]:
				postPref = np.array(post.preferences.list)
				score    = userPref @ postPref

				postNode = linked_list.PostNode(post, score)
				linkedList.add_node(postNode)

			postsList = linkedList.get_list_of_nodes()
			
			for post in watchedPosts.order_by('timeCreated').reverse()[:listSize - len(postsList)]:
				postsList.append(post.to_dict())
			
			return JsonResponse({"posts": postsList})
			
	except:
		print(" [ERROR]", sys.exc_info())
		return HttpResponse(status=500)

# Time to load   100 posts and    50 watched posts: 0.028502941131591797
# Time to load   200 posts and   100 watched posts: 0.016546010971069336
# Time to load   500 posts and   200 watched posts: 0.019222021102905273
# Time to load  1000 posts and   500 watched posts: 0.02732992172241211
# Time to load  2000 posts and  1000 watched posts: 0.04678010940551758
# Time to load  5000 posts and  2000 watched posts: 0.06942605972290039
# Time to load 10000 posts and  5000 watched posts: 0.18562102317810059
# Time to load 20000 posts and 10000 watched posts: 0.3571600914001465
# Time to load 50000 posts and 20000 watched posts: 0.7600769996643066

def following_feed(request):
	try:
		# Returns a list of posts made by all creators that a user is following. Starts looking through
		# all the posts that the user has not watched yet, and if there is room, fills in the rest of the
		# list with posts that the user did already watch. 
		if request.method == "GET":
			listSize  = 32
			user      = User.objects.get(uid=request.GET['uid'])
			postsList = list()

			watchedList = [watchedBy.post.postID for watchedBy in WatchedBy.objects.select_related("post").filter(user=user)]
			allowedPosts = Post.objects.filter(creator__followers__follower=user)

			notWatchedPosts = allowedPosts.exclude(postID__in=watchedList)
			watchedPosts    = allowedPosts.filter(postID__in=watchedList)

			for post in notWatchedPosts.order_by('timeCreated').reverse()[:listSize]:
				postsList.append(post.to_dict()) 

			for post in watchedPosts.order_by('timeCreated').reverse()[:listSize - len(postsList)]:
				postsList.append(post.to_dict())

			return JsonResponse({"posts": postsList})        

	except:
		print(" [ERROR]", sys.exc_info())
		return HttpResponse(status=500)

# Time to load    10 watched posts: 0.026569128036499023
# Time to load    20 watched posts: 0.01180410385131836
# Time to load    50 watched posts: 0.01366281509399414
# Time to load   100 watched posts: 0.01414179801940918
# Time to load   200 watched posts: 0.01628899574279785
# Time to load   500 watched posts: 0.02431488037109375
# Time to load  1000 watched posts: 0.08461523056030273
# Time to load  2000 watched posts: 0.06368684768676758
# Time to load  5000 watched posts: 0.17388391494750977
# Time to load 10000 watched posts: 0.3375213146209717
# Time to load 20000 watched posts: 0.7280130386352539