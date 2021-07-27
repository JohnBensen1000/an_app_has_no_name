import sys

import numpy as np

from firebase_admin import auth

from django.http import HttpResponse, JsonResponse
from django.apps import apps

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
			listSize   = 16
			user       = User.objects.get(uid=request.GET['uid'])
			userPref   = np.array(user.preferences.list)
			linkedList = linked_list.LinkedList()

			watchedList  = [watchedBy.post.postID for watchedBy in WatchedBy.objects.filter(user=user)    ]
			creatorsList = [following.creator     for following in Following.objects.filter(follower=user)]
			reportedList = [reported.post.postID  for reported  in Reported.objects.filter(user=user)     ]

			creatorsList.extend([blocked.creator for blocked in Blocked.objects.filter(user=user)])
		 
			notWatchedPosts = Post.objects.exclude(postID__in=watchedList).exclude(creator=user).exclude(creator__in=creatorsList).exclude(postID__in=reportedList)
			watchedPosts    = Post.objects.filter(postID__in=watchedList).exclude(creator=user).exclude(creator__in=creatorsList).exclude(postID__in=reportedList)

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

def following_feed(request):
    try:
        # Returns a list of posts made by all creators that a user is following. Starts looking through
        # all the posts that the user has not watched yet, and if there is room, fills in the rest of the
        # list with posts that the user did already watch. 
        if request.method == "GET":
            listSize    = 16
            user        = User.objects.get(uid=request.GET['uid'])
            followings  = [relationship.creator for relationship in Following.objects.filter(follower=user)]
            watchedList = [watchedBy.post.postID for watchedBy in WatchedBy.objects.filter(user=user)]

            postsList = list()

            notWatchedPosts = Post.objects.filter(creator__in=followings).exclude(postID__in=watchedList)
            watchedPosts    = Post.objects.filter(creator__in=followings, postID__in=watchedList)

            for post in notWatchedPosts.order_by('timeCreated').reverse()[:listSize]:
                postsList.append(post.to_dict()) 

            for post in watchedPosts.order_by('timeCreated').reverse()[:listSize - len(postsList)]:
                postsList.append(post.to_dict())   
                
            return JsonResponse({"posts": postsList})        

    except:
        print(" [ERROR]", sys.exc_info())
        return HttpResponse(status=500)