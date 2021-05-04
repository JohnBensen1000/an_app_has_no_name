import sys, json
import requests

from django.shortcuts import render
from user_profile.models import *
from demographics.models import *
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from google.oauth2 import id_token
import google.auth.transport

serverToken = 'AAAALGfgH5A:APA91bH1FgqgJOZ4LQds7XgnRxatrIxZgP9hzvx8MItG8fsgxDGAgR9XocFWh8qwNfCxBaj-eddA5DwS2r2SNRbNU2iOIJvu-QaXo_2aPf-DujhqdMhz9H3aW5ZItBfXuV0JZ5BGQXDV'

@csrf_exempt
def creators(request, searchString=None):
	try:
		# Recieves a string and returns a list of all users whose username contains the string. If 
		# no usernames contain this string, returns an empty list.
		if request.method == "GET":
			objectList  = UserProfile.objects.filter(username__icontains=searchString)
			creatorList = [{"username":user.username, "userID":user.userID} for user in objectList]

			if creatorList == []:
				return JsonResponse({"creatorsList": []})
			else:
				return JsonResponse({"creatorsList": creatorList})

	except:
		print(" [ERROR]", sys.exc_info())
		return HttpResponse(status=500)

@csrf_exempt 
def identifiers(request):
	try:
		# Checks is any unique identifiers have been taken for a user account. These unique identifiers
		# are: "userID", "email", and "phone". Returns a json object that assigns a boolean value to 
		# each field, true if it's taken, false otherwise. 
		if request.method == "POST":
			newUser = request.POST

			alreadyTaken = {
				"userID": UserProfile.objects.filter(userID=newUser["userID"]).exists(),
				"email": AccountInfo.objects.filter(email=newUser["email"]).exists(),
				"phone": AccountInfo.objects.filter(phone=newUser["phone"]).exists(),
			}
			return JsonResponse(alreadyTaken)

	except:
		print(" [ERROR]", sys.exc_info())
		return HttpResponse(status=500)

@csrf_exempt
def user(request, userID=None):
	try:
		# Recieves the userID for a user, and returns information about that user.
		if request.method == "GET":
			user     = UserProfile.objects.get(userID=userID)
			userJson = user.get_user_info_json()

			return JsonResponse(userJson)

		# Recieves a json object containing fields that correspond to a new user's account. First creates
		# two entities: userDemo and accountInfo, both of which will have a one-to-one relationship with
		# the new userProfile. Then creates a new UserProfile for the new user. 
		if request.method == "POST":
			newUser = request.POST

			token  = newUser["idToken"]
			idInfo = id_token.verify_firebase_token(token, google.auth.transport.requests.Request())

			userDemo    = Demographics.objects.create()
			accountInfo = AccountInfo.objects.create(
				email=newUser["email"],
				phone=newUser["phone"],
				preferredLanguage=newUser["preferredLanguage"],

			)
			UserProfile.objects.create(
				userID       = newUser["userID"],
				username     = newUser["username"],
				firebaseSub  = idInfo["sub"],
				accountInfo  = accountInfo,
				demographics = userDemo,
			)

			return HttpResponse(status=201)

		# Deletes the UserProfile entity and related AccountInfo and Demographics entities associated
		# with the recieved userID.
		elif request.method == "DELETE":
			user = UserProfile.objects.get(userID=userID)
			user.delete_user()
			return HttpResponse("Deleted user account")

	except:
		print(" [ERROR]", sys.exc_info())
		return HttpResponse(status=500)

@csrf_exempt
def profile(request, userID=None):
	# The profile attribute in the AccountInfo field contains information on a user's profile. A user's
	# profile could be an image, video, or non-existent. This information is used to determine whether
	# to create a profile for a user, and if the profile should be in image of video format. 

	try:
		# Gets the profile status of a a user's profile. 
		if request.method == "GET":
			user = UserProfile.objects.get(userID=userID)
			return JsonResponse({"profileType": user.accountInfo.profileType})

		# Updated the profile status of a user's profile.
		elif request.method == "POST":
			user = UserProfile.objects.get(userID=userID)
			user.accountInfo.profileType = request.POST["profileType"]
			user.accountInfo.save()

			return HttpResponse(status=201)

	except:
		print(" [ERROR]", sys.exc_info())
		return HttpResponse(status=500)


@csrf_exempt
def following_list(request, userID=None):
	try:
		# Returns a list of all the creators that a user is following.
		if request.method == "GET":	
			user = UserProfile.objects.get(userID=userID)
			return HttpResponse(user.get_followings())

	except:
		print(" [ERROR]", sys.exc_info())
		return HttpResponse(status=500)

@csrf_exempt
def following(request, userID=None, creatorID=None):
	# Handles the one way following relationship between a user and a creator. When a user starts
	# or stops (POST or DELETE, respectively) following another user, sends a push notification to 
	# the other user, updating the number of new followers that the other user has. 

	user    = UserProfile.objects.get(userID=userID)
	creator = UserProfile.objects.get(userID=creatorID)

	try:
		# Returns true if the user is currently following the creator, returns false otherwise.
		if request.method == "GET":
			return JsonResponse({"following_bool": (creator in user.get_followings())})

		# Most of the functionality in this section is based on what value the Boolean field, "newFollower",
		# in a Relationship entity should be. If "followBack" is a field in the POST body, then a user has 
		# decided to either follow back or not to follow back a new follower. Either way, set the newFollower 
		# field of the user-follower Relationship to False. If "followBack" is not a field in the POST body, 
		# then create a new Relationship entity. Set "newFollower" to True if the creator does not currently 
		# follow the user.
		if request.method == "POST":
			if "followBack" in request.POST:
				if request.POST['followBack'] == 'true':
					Relationships.objects.create(
						follower    = user, 
						creator     = creator, 
						newFollower = False
					)

				followingRel = Relationships.objects.get(follower=creator, creator=user)
				followingRel.newFollower = False
				followingRel.save()

			else:
				newFollower = not Relationships.objects.filter(follower=creator, creator=user).exists()
				Relationships.objects.create(
					follower    = user, 
					creator     = creator, 
					newFollower = newFollower
				)

			send_new_followers(creator)
			return HttpResponse(status=201)	

		if request.method == "DELETE":
			Relationships.objects.get(follower=user, creator=creator).delete()

			send_new_followers(creator)
			return HttpResponse(status=201)

	except:
		print(" [ERROR]", sys.exc_info())
		return HttpResponse(status=500)

def send_new_followers(userProfile):
	# Sends a push notification to a user with a list of all of their new followers. Sends
	# notification through google firebase to a device (identified by userProfile.deviceToken).

	headers = {
		'Content-Type': 'application/json',
		'Authorization': 'key=' + serverToken,
	}
	body = {
		'notification': {
			'body': {"userID": userProfile.userID, "new_followers": userProfile.get_followers()}
		},
		'to': userProfile.deviceToken,
		'priority': 'high',
	}
	response = requests.post("https://fcm.googleapis.com/fcm/send", headers=headers, data=json.dumps(body))

@csrf_exempt
def followers(request, userID=None):
	try:
		# Returns a list of all of the user's new followers. Only looks at users that are 
		# currently following the user with the field "newFollower" set to True.

		if request.method == "GET":
			user = UserProfile.objects.get(userID=userID)

			allFollowersObjects = [relation.follower for relation in 
				user.followers.filter(relation=Relationships.following).filter(newFollower=True)]
			
			allFollowers = [{"username":follower.username, "userID":follower.userID} 
            	for follower in allFollowersObjects]

			return JsonResponse({'new_followers' : allFollowers})
 
	except:
		print(" [ERROR]", sys.exc_info())
		return HttpResponse(status=500)

@csrf_exempt
def friends(request, userID=None):
	try:
		# Returns a list of all of the user's friends.
		if request.method == "GET":
			user = UserProfile.objects.get(userID=userID)
			return JsonResponse({'friends' : user.get_friends()})

	except:
		print(" [ERROR]", sys.exc_info())
		return HttpResponse(status=500)

