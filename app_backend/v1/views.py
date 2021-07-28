import sys
import json
import os
import ssl
import smtplib
import datetime

import numpy as np

from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse
from django.apps import apps

from better_profanity import profanity

from google.cloud import firestore
from google.cloud import storage, firestore, vision

db = firestore.Client()

import firebase_admin
from firebase_admin import messaging

default_app = firebase_admin.initialize_app()

# firestore.initialize_app()

serverToken = 'AAAAsEEDk0k:APA91bF1sOQc-E_MFIW9IEDjpELLj3euKlPzAGBfwARrKgX199yD8VrDyx6q5omEkxlzIuK_fU6jb-rAsiRTimhaFtpfq_mXzSZ322PsiMZ65GxFWoIT2lk3ZhwZzJ_Q-MI-E_jMAZo1'

User          = apps.get_model("models", "User")
Preferences   = apps.get_model("models", "Preferences")
Profile       = apps.get_model("models", "Profile")
Post          = apps.get_model("models", "Post")
Following     = apps.get_model("models", "Following")
Blocked       = apps.get_model("models", "Blocked")
WatchedBy     = apps.get_model("models", "WatchedBy")
Reported      = apps.get_model("models", "Reported")
ChatMember    = apps.get_model("models", "ChatMember")
Chat          = apps.get_model("models", "Chat")

client = storage.Client(project=os.getenv("CLIENT"))
bucket = client.get_bucket(os.getenv("BUCKET"))

visionClient = vision.ImageAnnotatorClient()

@csrf_exempt
def access(request):
    try:
        if request.method == "GET":
            if request.GET['accessCode'] == "access-token12":
                return JsonResponse({'accessGranted': True})
            else:
                return JsonResponse({'accessGranted': False})

    except:
        print(" [ERROR]", sys.exc_info())
        return HttpResponse(status=500)

@csrf_exempt
def signedInStatus(request, uid=None):
	try:
		# Lets user sign-in/sign-out of their account. If a user signs into their account, the 
		# field "deviceToken" is updated to whatever device the user signed in from. Signs out 
		# all other users that are signed in on this device If a user is signing out of their 
		# account, "deviceToken" is set to "" to indicate that the user is not signed in on 
		# any device.
		if request.method == "POST":
			requestBody = json.loads(request.body)

			user = User.objects.get(uid=uid)

			if requestBody['signIn'] == True:
				for tempUser in User.objects.filter(deviceToken=requestBody["deviceToken"]):
					tempUser.signedIn    = False
					tempUser.deviceToken = ""
					tempUser.save()
					
				user.deviceToken = requestBody["deviceToken"] 
				user.signedIn    = True

			else:
				user.deviceToken = ""
				user.signedIn    = False

			user.save()

			return JsonResponse({'isSignedIn': user.signedIn, 'user': user.to_dict()}, status=201)

	except:
		print(" [ERROR]", sys.exc_info())
		return HttpResponse(status=500)

@csrf_exempt
def deviceSignedInOn(request):
	try:
		# Checks to see if anyone is signed on the given device (identified by 'deviceToken'). This 
		# is used so that a user doesn't have to sign into their account every time they open the app. 
		# If a user is signed in on the given device, then returns the uid of that user. 
		if request.method == "GET":
			deviceToken = request.GET["deviceToken"]
			if User.objects.filter(deviceToken=deviceToken).exists():
				return JsonResponse({
					"signedIn": True,
					"user": User.objects.get(deviceToken=deviceToken).to_dict()
				})
			else:
				return JsonResponse({
					"signedIn": False
				})

	except:
		print(" [ERROR]", sys.exc_info())
		return HttpResponse(status=500)

@csrf_exempt
def chats(request, uid=None):
    try:
        # Returns a list of the chatIDs of each chat that a user is part of. Sorts by the how
        # recent the last chat item was sent in a chat. 
        if request.method == "GET":
            chatIdList = [chatMember.chat.chatID for chatMember in ChatMember.objects.filter(member__uid=uid)]
            chatList   = list()

            for chat in Chat.objects.filter(chatID__in=chatIdList).order_by("-lastChatTime"):
                chatMember            = ChatMember.objects.filter(member__uid=uid).filter(chat__chatID=chat.chatID).first()
                chatDict              = chat.to_dict()
                chatDict['isUpdated'] = chatMember.isUpdated

                chatList.append(chatDict)

            return JsonResponse({"chats": chatList})

    except:
        print(" [ERROR]", sys.exc_info())
        return HttpResponse(status=500)

@csrf_exempt
def chat(request, uid=None, chatID=None):
    try:
        # Handles posting a new chat. A new chat could be a text or a post (image/video). If the new chat is
        # a post, then checks if the post is NSFW. If it isn't, saves the post in the appropriate location in 
        # google storage. Then creates a new document in google firestore (in the correct collection), 
        # documenting the sender and location of the post. If the new chat is a text, then checks if it contains
        # profanity. If it doesn't, then stores the chat and sender in a new document in google firestore (in 
        # the correct collection). Saves the chat object, forcing it to update it's field "lastChatTime".
        
        if request.method == "POST":
            newChatJson = json.loads(request.body)

            docRef = db.collection('CHATS').document(chatID).collection("chats").document()

            if newChatJson['isPost']:
                docRef.set({
                    'uid':    uid,
                    'time':   firestore.SERVER_TIMESTAMP,
                    'isPost': True,
                    'post':   {
                        'downloadURL': newChatJson['downloadURL'],
                        'isImage':     newChatJson['isImage']
                    }
                })
            else:
                docRef.set({
                    'uid':    uid,
                    'time':   firestore.SERVER_TIMESTAMP,
                    'isPost': False,
                    'text':   newChatJson['text']
                })

            chat = Chat.objects.get(chatID=chatID)
            chat.save()

            for chatMember in ChatMember.objects.filter(chat=chat).exclude(member__uid=uid):
                chatMember.isUpdated = False
                chatMember.save()

                if chatMember.member.deviceToken is not None:
                    message = messaging.Message(data={'chatID': chatID}, token=chatMember.member.deviceToken)
                    messaging.send(message)
            
            return JsonResponse({"reasonForRejection": None}, status=201)
            
    except:
        print(" [ERROR]", sys.exc_info())
        return HttpResponse(status=500)

@csrf_exempt
def updated(request, uid=None, chatID=None):
    try:
        # This view exists to let a client tell the database that they have read all the most recent
        # chat items in a particular chat. 
        if request.method == "POST":
            chatMember = ChatMember.objects.filter(chat__chatID=chatID).filter(member__uid=uid).first()
            chatMember.isUpdated = True
            chatMember.save()

            return HttpResponse(status=200)

    except:
        print(" [ERROR]", sys.exc_info())
        return HttpResponse(status=500)

@csrf_exempt
def report(request, uid=None, chatID=None):
    try:
        # When a user reports a chat item, sends an email to the development account with the
        # json object containing the chat item, the chat ID, and the uid of the user who reported 
        # the chat item. 
        if request.method == "POST":
            chat        = Chat.objects.get(chatID=chatID)
            user        = User.objects.get(uid=uid)
            requestBody = json.loads(request.body)

            port    = 465 
            context = ssl.create_default_context()

            with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
                server.login("entropy.developer1@gmail.com", "CominG1$is@Winter6*9sNow11")
                server.sendmail(
                    "entropy.developer1@gmail.com", 
                    "entropy.developer1@gmail.com", 
                    """
                        %s

                        Chat item: %s
                        Chat: %s
                        Reporting user uid: %s
                    """ % (os.getenv("ENVIRONMENT"), json.dumps(requestBody["chatItem"]), chat.chatID, user.uid)
                )

            return HttpResponse(status=200)

    except:
        print(" [ERROR]", sys.exc_info())
        return HttpResponse(status=500)

@csrf_exempt
def members(request, uid=None, chatID=None):
    try:
        chat = Chat.objects.get(chatID=chatID)

        # Returns a list of all members in a chat. 
        if request.method == "GET":
            membersList = list()
            for chatMember in ChatMember.objects.filter(chat=chat):
                membersList.append(chatMember.member.to_dict())

            return JsonResponse({
                'membersList': membersList
            })

    except:
        print(" [ERROR]", sys.exc_info())
        return HttpResponse(status=500)

@csrf_exempt
def comments(request, postID=None):
    try:
        # Recieves a json object with three fields: "comment", "uid", and "path". "comment" contains 
        # the actual comment itself. If the comment contains profanity, returns a json response telling the
        # client that the comment contains profanity. "uid" is the uid of the user who posted the comment. 
        # "path" is the directory of where the new comment will be stored in the firestore database. The 
        # "path" string will be stored in the database so that when someone posts a comment responding to 
        # this comment, the new comment will know where to be placed in the database.    
        
        if request.method == "POST":
            requestJson = json.loads(request.body)

            if profanity.contains_profanity(requestJson["comment"]):
                return JsonResponse({"reasonForDenial": "profanity"}, status=200)

            path          = requestJson["path"] + "/c/" + str(int(datetime.datetime.now().timestamp()))
            commentDocRef = db.document('COMMENTS' + "/%d" % postID + path)

            commentDocRef.set({
                u'datePosted': firestore.SERVER_TIMESTAMP,
                u'uid':        requestJson["uid"],
                u'comment':    requestJson["comment"],
                u'path':       path,
            })
            return JsonResponse({"reasonForDenial": None}, status=201)

        # Gets a list of the comments of a post. 
        if request.method == "GET":
            uid  = request.GET["uid"]
            user = User.objects.get(uid=uid)

            postDoc      = db.collection('COMMENTS').document(str(postID))
            collection   = postDoc.collection("c")
            commentsList = get_all_comments(user, collection, 0)

            return JsonResponse({'comments': commentsList})

    except:
        print(" [ERROR]", sys.exc_info())
        return HttpResponse(status=500)

def get_all_comments(user, collection, level):
    # Comments are stored such that each response comment is stored in a collection 
    # that is under the parent comment. Therefore, this function recursively gets
    # to every comment and creates a list of all comments. Does not return comments
    # from users who deleted their accounts or who the current user is currently blocking.

    allComments = []

    for commentDoc in collection.order_by('datePosted').stream():
        commentDict = commentDoc.to_dict()
        creator     = User.objects.filter(uid=commentDict["uid"]).first()

        if creator is not None and not Blocked.objects.filter(user=user, creator=creator).exists():
            commentDict["level"] = level
            del commentDict["datePosted"]

            subCollection = collection.document(commentDoc.id).collection("c")

            subComments = get_all_comments(user, subCollection, level + 1)
            commentDict['numSubComments'] = len(subComments)
            allComments.append(commentDict)
            if len(subComments) > 0:
                allComments.extend(subComments)

    return allComments

@csrf_exempt
def report(request, postID):
    try:
        if request.method == "POST":
            send_reported_comment_email(postID, json.loads(request.body))
            return HttpResponse(status=201)

    except:
        print(" [ERROR]", sys.exc_info())
        return HttpResponse(status=500)

def send_reported_comment_email(postID, commentJson):
	port    = 465 
	context = ssl.create_default_context()

	with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
		server.login("entropy.developer1@gmail.com", "CominG1$is@Winter6*9sNow11")
		server.sendmail(
			"entropy.developer1@gmail.com", 
			"entropy.developer1@gmail.com", 
			"""
                %s

				Comment: %s
			 	Comment path: %s
				Post ID: %s
			""" % (os.getenv("ENVIRONMENT"), commentJson["comment"], commentJson["path"], postID)
		)

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
		# the user has created or has reported.

		if request.method == "GET":
			listSize   = 16
			user       = User.objects.get(uid=uid)
			userPref   = np.array(user.preferences.list)
			linkedList = LinkedList()

			watchedList  = [watchedBy.post.postID for watchedBy in WatchedBy.objects.filter(user=user)    ]
			creatorsList = [following.creator     for following in Following.objects.filter(follower=user)]
			reportedList = [reported.post.postID  for reported in Reported.objects.filter(user=user)      ]

			creatorsList.extend([blocked.creator for blocked in Blocked.objects.filter(user=user)])
		
			postQuerySet    = Post.objects.exclude(isFlagged=True).exclude(creator=user).exclude(creator__in=creatorsList).exclude(postID__in=reportedList)
			notWatchedPosts = postQuerySet.exclude(postID__in=watchedList)
			watchedPosts    = postQuerySet.filter(postID__in=watchedList)

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

def following_content(request, uid=None):
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

			postQuerySet    = Post.objects.filter(creator__in=followings).exclude(isFlagged=True)
			notWatchedPosts = postQuerySet.exclude(postID__in=watchedList)
			watchedPosts    = postQuerySet.filter(postID__in=watchedList)

			for post in notWatchedPosts.order_by('timeCreated').reverse()[:listSize]:
				postsList.append(post.to_dict()) 

			for post in watchedPosts.order_by('timeCreated').reverse()[:listSize - len(postsList)]:
				postsList.append(post.to_dict())   

			return JsonResponse({"posts": postsList})        

	except:
		print(" [ERROR]", sys.exc_info())
		return HttpResponse(status=500)

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

		# Returns a list of all of a user's posts. Only returns posts that aren't flagged. 
		if request.method == "GET":
			userPostsList = []
			for post in user.created.all().order_by('-timeCreated'):
				if not post.isFlagged:
					userPostsList.append(post.to_dict())	
					
			return JsonResponse({"posts": userPostsList})

		# Receives meta-data about a post and the post's image or video file. Uses google vision to
		# determine if the post is NSFW or not. If it is, returns a Json object informing the client
		# that the post has been rejected due to being NSFW. Otherwise, creates a new post entity and 
		# uploads the post file to google storage in the right location and with the right file 
		# extension and content type. 
		if request.method == "POST":
			postID             = str(int(100 * datetime.datetime.now().timestamp()))
			newPostJson        = json.loads(request.body)
			reasonForRejection = None

			post = Post.objects.create(
				postID      = postID,
				preferences = Preferences.objects.create(),
				creator     = user,
				isImage	    = newPostJson["isImage"],
				isPrivate   = newPostJson["isPrivate"],
				downloadURL = newPostJson["downloadURL"]
			)

			if not check_if_post_is_safe(newPostJson['downloadURL']):
				post.isFlagged = True
				post.save()
				
				reasonForRejection = "NSFW"
				send_reported_content_email(post)

			return JsonResponse({"reasonForRejection": reasonForRejection}, status=201)

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

		# Allows a user to upload a new image/video as their profile. Uses google vision to check
		# if the profile image/video is safe. If it is, then saves the picture/video in google storage
		# and updates the user's profile entity. 
		elif request.method == "POST":
			profileJson        = json.loads(request.body)
			reasonForRejection = None

			user = User.objects.get(uid=uid)
			user.profile.exists      = True
			user.profile.isImage     = profileJson["isImage"]
			user.profile.downloadURL = profileJson['downloadURL']
			user.profile.save()

			if not check_if_post_is_safe(profileJson['downloadURL']):
				user.profile.isFlagged = True
				user.profile.save()

				reasonForRejection = "NSFW"

				port    = 465 
				context = ssl.create_default_context()
				with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
					server.login("entropy.developer1@gmail.com", "CominG1$is@Winter6*9sNow11")
					server.sendmail(
						"entropy.developer1@gmail.com", 
						"entropy.developer1@gmail.com", 
						"""
							%s

							Reported user id: %s
							profile pk: %s
							Download URL: %s
						""" % (os.getenv("ENVIRONMENT"), user.uid, user.profile.pk, user.profile.downloadURL)
					)

			return JsonResponse({"reasonForRejection": reasonForRejection}, status=201)

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
def reports(request, uid=None):
	try:
		# If the user reports an indivudal post, sends an email to the administrator
		# with the post's details. The administrator can then decide whether to delete
		# the post or not. Also created a new report entity that contains the user that
		# reported the post and the post itself. 

		if request.method == "POST":
			requestBody = json.loads(request.body)

			post = Post.objects.get(postID=requestBody["postID"])
			user = User.objects.get(uid=uid)

			Reported.objects.create(user=user, post=post)

			send_reported_content_email(post)

			return HttpResponse(status=201)
	except:
		print(" [ERROR]", sys.exc_info())
		return HttpResponse(status=500)

@csrf_exempt
def reports_profile(request, uid=None):
	try:
		if request.method == "POST":
			user         = User.objects.get(uid=uid)
			requestBody  = json.loads(request.body)
			reportedUser = User.objects.get(uid=requestBody["reportedUser"])
			profile      = reportedUser.profile

			port    = 465 
			context = ssl.create_default_context()

			with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
				server.login("entropy.developer1@gmail.com", "CominG1$is@Winter6*9sNow11")
				server.sendmail(
					"entropy.developer1@gmail.com", 
					"entropy.developer1@gmail.com", 
					"""
						%s

						Reported user id: %s
						Download URL: %s
						Reporting user id: %s
					""" % (os.getenv("ENVIRONMENT"), reportedUser.uid, profile.downloadURL, user.uid)
				)

				return HttpResponse(status=200)

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

def check_if_post_is_safe(downloadURL):
	image                  = vision.Image()
	image.source.image_uri = downloadURL
	safe                   = visionClient.safe_search_detection(image=image).safe_search_annotation

	for safeAttribute in [safe.adult, safe.medical, safe.violence]:
		if safeAttribute.value >= 5:
			return False

	return True

def create_new_direct_message(user1, user2):
    chat = Chat.objects.create(
        isDirectMessage=True
    )
    
    ChatMember.objects.create(
        isOwner = True,
        chat    = chat,
        member  = user1
    )
    ChatMember.objects.create(
        isOwner = True,
        chat    = chat,
        member  = user2
    )

@csrf_exempt
def followings(request, uid=None):
    try:
        user = User.objects.get(uid=uid)

        # Returns a list of all creators that a user is following. Shows if each creator is a 
        # friend of the user or not. 
        if request.method == "GET":
            followingsList = list()
            for following in Following.objects.filter(follower=user):
                creator = following.creator
                followingsList.append({
                    "user":     creator.to_dict(),
                    "isFriend": Following.objects.filter(follower=creator, creator=user).exists()
                })

            return JsonResponse({"followings": followingsList})

        # Creates a relationship entity that stores the fact that a user is following a creator. The 
        # creator is identified by 'uid' given in the request body. 'newFollower' is a field in 
        # Relationship that keeps track of whether or not to notify a creator that a new user started
        # following them. This will only be set to True if the creator is not already following that 
        # new user. Deletes
        if request.method == "POST":
            requestBody = json.loads(request.body)
            creator     = User.objects.get(uid=requestBody['uid'])
            isNewFriend = Following.objects.filter(follower=creator, creator=user).exists()

            if Blocked.objects.filter(user=user, creator=creator).exists():
                Blocked.objects.filter(user=user, creator=creator).delete()

            Following.objects.create(
                follower    = user,
                creator     = creator,
                newFollower = not isNewFriend, 
            )

            if isNewFriend:
                create_new_direct_message(user, creator)
            else:
                pass
                # send_new_followers(creator)

            return HttpResponse(status=201)	

    except:
        print(" [ERROR]", sys.exc_info())
        return HttpResponse(status=500)

@csrf_exempt
def blocked(request, uid=None):
    try:
        # Returns a list of all creators that the user is blocking.
        if request.method == "GET":
            user        = User.objects.get(uid=uid)
            blockedList = [blocked.creator.to_dict() for blocked in Blocked.objects.filter(user=user)]

            return JsonResponse({"blocked": blockedList})

        # Creates a blocked relationship between two users. Deletes the following relationship
        # and direct message between the two users if they exist.
        if request.method == "POST":
            requestBody = json.loads(request.body)
            user        = User.objects.get(uid=uid)
            creator     = User.objects.get(uid=requestBody['uid'])  

            if Following.objects.filter(follower=user, creator=creator).exists():
                Following.objects.filter(follower=user, creator=creator).delete()

            Blocked.objects.create(
                user    = user,
                creator = creator,
            )

            delete_direct_messages_if_exists(user, creator)

            return HttpResponse(status=201)

    except:
        print(" [ERROR]", sys.exc_info())
        return HttpResponse(status=500)      

@csrf_exempt
def blocked_user(request, uid=None, creator_uid=None):
    try:
        # Deletes a blocked relationship between two users.
        if request.method == "DELETE":
            user        = User.objects.get(uid=uid)
            creator     = User.objects.get(uid=creator_uid)

            Blocked.objects.filter(user=user, creator=creator).delete()

            return HttpResponse(status=200)

    except:
        print(" [ERROR]", sys.exc_info())
        return HttpResponse(status=500)     

# def send_new_followers(user):
# 	# Sends a push notification to a user with a list of all of their new followers. Sends
# 	# notification through google firebase to a device (identified by userProfile.deviceToken).

#     newFollowers = [relation.follower.to_dict() for relation in Following.objects.filter(newFollower=True, creator=user)]

#     headers = {
#         'Content-Type': 'application/json',
#         'Authorization': 'key=' + serverToken,
#     }
#     body = {
#         'notification': {
#             'body': {"uid": user.uid, "new_followers": newFollowers}
#         },
#         'to': user.deviceToken,
#         'priority': 'high',
#     }
#     response = requests.post("https://fcm.googleapis.com/fcm/send", headers=headers, data=json.dumps(body))


@csrf_exempt
def following(request, uid0=None, uid1=None):
    try:
        follower  = User.objects.get(uid=uid0)
        creator   = User.objects.get(uid=uid1)

        # Checks to see if a user (identified by uid0) is followering another user (identified by uid1)
        if request.method == "GET":
            isFollowing = Following.objects.filter(follower=follower, creator=creator).exists()
            return JsonResponse({"isFollowing": isFollowing})

        # Allows a user to follow back or not follow back a new follower. Either way, the user's new
        # follower will no longer be labeled as a new follower. Checks to see if the following relationship
        # doesn't already exist before creating a new one. Returns a 201 status code if the user decides 
        # to follow back, returns 200 otherwise. 
        if request.method == "POST":
            following             = Following.objects.get(follower=follower, creator=creator)
            following.newFollower = False
            following.save()

            requestBody = json.loads(request.body)

            if requestBody['followBack'] and not Following.objects.filter(follower=creator, creator=follower).exists():
                Following.objects.create(
                    follower    = creator,
                    creator     = follower,
                    newFollower = False, 
                )
                create_new_direct_message(follower, creator)

                return HttpResponse(status=201)
            else:
                return HttpResponse(status=200)

        # Deletes a one-way following relationship. If follower is friends with the creator, then
        # deletes the direct message between the two. This includes deleting the chat data in 
        # firestore and the chat entity in the database. 
        if request.method == "DELETE":
            delete_direct_messages_if_exists(follower, creator)

            following = Following.objects.get(follower=follower, creator=creator)
            following.delete()

            return HttpResponse(status=200)

    except:
        print(" [ERROR]", sys.exc_info())
        return HttpResponse(status=500)

@csrf_exempt
def followers(request, uid=None):
    try:
        # Returns a list of all of a user's (identified by uid) followers.
        if request.method == "GET":
            user         = User.objects.get(uid=uid)
            followerList = list() 
            for relationship in Following.objects.filter(creator=user):
                followerList.append(relationship.follower.to_dict())

            return JsonResponse({'followerList': followerList})

    except:
        print(" [ERROR]", sys.exc_info())
        return HttpResponse(status=500)

@csrf_exempt
def new_followers(request, uid=None):
    try:
        # Returns a list of all of a user's (identified by uid) new followers.
        if request.method == "GET":
            user         = User.objects.get(uid=uid)
            followerList = list() 
            for relationship in Following.objects.filter(creator=user, newFollower=True):
                followerList.append(relationship.follower.to_dict())

            return JsonResponse({'followerList': followerList})
    except:
        print(" [ERROR]", sys.exc_info())
        return HttpResponse(status=500)

@csrf_exempt
def friends(request, uid=None):
    try:
        # Returns a list of all a user's friends. A 'friend' is defined as another user that
        # both follows and is followed by a user. 
        if request.method == "GET":
            user        = User.objects.get(uid=uid)
            friendsList = list() 

            for relationship in Following.objects.filter(creator=user):
                follower = relationship.follower
                if Following.objects.filter(creator=follower, follower=user):
                    friendsList.append(follower.to_dict())

            return JsonResponse({'friendsList': friendsList})

    except:
        print(" [ERROR]", sys.exc_info())
        return HttpResponse(status=500)

def delete_direct_messages_if_exists(follower, creator):
    if Following.objects.filter(follower=creator, creator=follower).exists():
        chatDict = dict()

        for chatMember in ChatMember.objects.filter(member=follower):
            if chatMember.chat.isDirectMessage:
                chatDict[chatMember.chat] = True

        for chatMember in ChatMember.objects.filter(member=creator):
            if chatMember.chat in chatDict:
                chat = chatMember.chat

                docRef = db.collection('CHATS').document(chat.chatID)
                colRef = docRef.collection("chats")
                for doc in colRef.stream():
                    doc.reference.delete()

                docRef.delete()
                chat.delete()

@csrf_exempt
def userIdTaken(request):
	try:
		# Recieves a user id and checks if it is taken by another user.
		if request.method == "GET":
			userID        = request.GET["userID"]
			isUserIdTaken = User.objects.filter(userID=userID).exists()

			return JsonResponse({"isUserIdTaken": isUserIdTaken})

	except:
		print(" [ERROR]", sys.exc_info())
		return HttpResponse(status=500)

@csrf_exempt
def search(request, uid=None):
	try:
		# Recieves a string and returns a list of all users whose userID contains the string. 
		# Return any creators that the user (identified by uid) is currently blocking.
		
		if request.method == "GET":
			user         = User.objects.get(uid=uid)
			searchString = request.GET["contains"]

			if searchString == '':
				return JsonResponse({"creatorsList": []})

			objectList   = User.objects.filter(userID__icontains=searchString)
			creatorsList = list()

			for creator in objectList:
				if not Blocked.objects.filter(user=user, creator=creator).exists() and creator.uid != user.uid:
					creatorsList.append(creator.to_dict())

			if creatorsList == []:
				return JsonResponse({"creatorsList": []})
			else:
				return JsonResponse({"creatorsList": creatorsList})

	except:
		print(" [ERROR]", sys.exc_info())
		return HttpResponse(status=500)
		
@csrf_exempt
def preferences(request):
	try:
		# Simply returns a list of all fields found in the Preferences class. 
		if request.method == "GET":
			return JsonResponse({"fields": Preferences().fields})

	except:
		print(" [ERROR]", sys.exc_info())
		return HttpResponse(status=500)

@csrf_exempt
def new_user(request):
	try:
		# Recieves a json object containing fields that correspond to a new user's account. First checks to
		# see if any unique fields (userID, email, and phone) have been taken by another user. If any of these
		# fields have been taken, returns a list of the taken fields. If not, then creates a new User entity. 
		if request.method == "POST":
			# return HttpResponse(status=500)
			
			newUser = json.loads(request.body)

			fieldsTaken = list()
			for uniqueField in ["userID", "email", "uid"]:
				filter              = {}
				filter[uniqueField] = newUser[uniqueField]

				if User.objects.filter(**filter).exists():
					fieldsTaken.append(uniqueField)

			if len(fieldsTaken) > 0:
				return JsonResponse({"fieldsTaken": fieldsTaken}, status=200)

			else:
				user = User.objects.create(
					userID      = newUser["userID"],
					email       = newUser['email'],
					uid         = newUser["uid"],
					username    = newUser["username"],
					preferences = Preferences.objects.create(),
					profile     = Profile.objects.create(),
				)

				return JsonResponse({'user': user.to_dict()}, status=201)

	except:
		print(" [ERROR]", sys.exc_info())
		return HttpResponse(status=500)

@csrf_exempt
def user(request, uid=None):
	try:
		user = User.objects.get(uid=uid)

		# Recieves the uid for a user, and returns information about that user.
		if request.method == "GET":
			return JsonResponse({'user': user.to_dict()})


		if request.method == "POST":
			newData = json.loads(request.body)

			if 'profileColor' in newData:
				user.profileColor = newData['profileColor'] 
			if 'username' in newData:
				user.username = newData['username']
			user.save()

			return HttpResponse(status=201)

		# When deleting a user account, the Preference and Profile models that are associated with
		# it have to also be deleted. the method, delete_account(), takes care of that. 
		if request.method == "DELETE":
			for chatMember in ChatMember.objects.filter(member=user):
				if chatMember.chat.isDirectMessage:
					chatMember.chat.delete()
				chatMember.delete()

			if os.getenv("ENVIRONMENT") == "PRODUCTION":
				firebase_admin.auth.delete_user(user.uid)
			user.delete_account()
			return HttpResponse(status=200)
			
	except:
		print(" [ERROR]", sys.exc_info())
		return HttpResponse(status=500)

@csrf_exempt
def user_preferences(request, uid=None):
	try:
		user = User.objects.get(uid=uid)

		# Recieves a list of preference field names. If that field has a value less than .9, sets
		# it's value to .9.
		if request.method == "POST":
			newPreferences  = json.loads(request.body)

			for preference in newPreferences['preferences']:
				if user.preferences.__dict__[preference] < .9:
					user.preferences.__dict__[preference] = .9

			user.preferences.save()

			return HttpResponse(status=201)

	except:
		print(" [ERROR]", sys.exc_info())
		return HttpResponse(status=500)