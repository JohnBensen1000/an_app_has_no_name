import sys

import numpy as np

from firebase_admin import auth

from django.http import HttpResponse, JsonResponse
from django.apps import apps

User          = apps.get_model("models", "User")
Preferences   = apps.get_model("models", "Preferences")
Profile       = apps.get_model("models", "Profile")
Post          = apps.get_model("models", "Post")
Following     = apps.get_model("models", "Following")
Blocked       = apps.get_model("models", "Blocked")
WatchedBy     = apps.get_model("models", "WatchedBy")

class PostNode:
	def __init__(self, post, score):
		self.post  = post
		self.score = score
		self.next  = None
		self.prev  = None

class LinkedList:
	def __init__(self, maxSize=128):
		self.head    = None
		self.tail    = None
		self.size    = 0
		self.maxSize = maxSize

	def add_node(self, newNode):
		if self.head is None:
			self.head = newNode

		elif self.tail is None:
			self.__add_tail(newNode)

		elif newNode.score > self.head.score:
			self.__add_new_head(newNode)

		else:
			self.__insert_node_after_head(newNode)

		self.size += 1

		if self.size > self.maxSize:
			self.__remove_last_node()

	def get_list_of_nodes(self):
		listOfNodes = list()
		searchNode  = self.head

		for i in range(self.size):
			if searchNode is None:
				break

			listOfNodes.append(searchNode.post.to_dict())  
			searchNode = searchNode.next

		return listOfNodes

	def __add_tail(self, newNode):
		if newNode.score < self.head.score:
			self.tail      = newNode
			self.head.next = newNode
			self.tail.prev = self.head

		else:
			self.tail      = self.head
			self.tail.prev = newNode
			self.head      = newNode
			self.head.next = self.tail

	def __add_new_head(self, newNode):
		newNode.next   = self.head
		self.head.prev = newNode
		self.head      = newNode

	def __insert_node_after_head(self, newNode):
		searchNode = self.head
		while searchNode is not None and searchNode.score >= newNode.score:
			searchNode = searchNode.next

		if searchNode:
			newNode.next         = searchNode
			newNode.prev         = searchNode.prev
			searchNode.prev.next = newNode
			searchNode.prev      = newNode

		else:
			newNode.prev   = self.tail
			self.tail.next = newNode
			self.tail      = newNode

	def __remove_last_node(self):
		self.tail      = self.tail.prev
		self.tail.next = None
		self.size     -= 1

def recommendations(request, uid=None):
	try:
		# Returns a list of recommended posts for the user. At first, create a list of all posts that 
		# the user has not watched yet. This list of posts is ordered based on the dot product between 
		# the post's preference list and the user's preference list. If there is still space in the post 
		# list, fills in the rest of the list with posts that theuser did already watch (these posts 
		# are orderd based on when they were created). The list of post does not include posts from 
		# creators that the user isfollowing or is blocking. The list also does not include posts that
		# the user has created. 

		if request.method == "GET":
			listSize   = 16
			user       = User.objects.get(uid=uid)
			userPref   = np.array(user.preferences.list)
			linkedList = LinkedList()

			watchedList  = [watchedBy.post.postID for watchedBy in WatchedBy.objects.filter(user=user)]
			creatorsList = [following.creator for following in Following.objects.filter(follower=user)]
			creatorsList.extend([blocked.creator for blocked in Blocked.objects.filter(user=user)])
		 
			notWatchedPosts = Post.objects.exclude(postID__in=watchedList).exclude(creator=user).exclude(creator__in=creatorsList)
			watchedPosts    = Post.objects.filter(postID__in=watchedList).exclude(creator=user).exclude(creator__in=creatorsList)

			for post in notWatchedPosts.order_by('timeCreated').reverse()[:listSize]:
				postPref = np.array(post.preferences.list)
				score    = userPref @ postPref

				postNode = PostNode(post, score)
				linkedList.add_node(postNode)

			postsList = linkedList.get_list_of_nodes()
			
			for post in watchedPosts.order_by('timeCreated').reverse()[:listSize - len(postsList)]:
				postsList.append(post.to_dict())
			
			return JsonResponse({"posts": postsList})

	except:
		print(" [ERROR]", sys.exc_info())
		return HttpResponse(status=500)

def following(request, uid=None):
	try:
		# Returns a list of posts made by all creators that a user is following. Starts looking through
		# all the posts that the user has not watched yet, and if there is room, fills in the rest of the
		# list with posts that the user did already watch. 
		if request.method == "GET":
			listSize    = 16
			user        = User.objects.get(uid=uid)
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

