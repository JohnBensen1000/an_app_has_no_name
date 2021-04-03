import sys, json

from django.shortcuts import render
from user_profile.models import UserProfile, AccountInfo, Relationships
from demographics.models import *
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods


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
		print(" [ERROR]", sys.exc_info()[0])
		return HttpResponse(status=500)

@csrf_exempt
def user(request, userID=None):
	try:
		# Recieves the userID for a user, and returns information about that user.
		if request.method == "GET":
			user     = UserProfile.objects.get(userID=userID)
			userJson = user.get_user_info_json()

			return JsonResponse(userJson)

		# Recieves a json object containing fields that correspond to a new user's account. The fields of 
		# the json object will be: "userID", "email", "phone", "preferredLangauge", "username". The fields 
		# "userID", "email", and "phone" are all unique identifiers, so if the value provided for one or 
		# more of these is already taken by another user, a list of all taken fields will be returned. If 
		# none of these fields are taken, then a new account is created with the given values. 
		if request.method == "POST":
			newUser = request.POST

			alreadyTaken = {
				"userID": UserProfile.objects.filter(userID=newUser["userID"]).exists(),
				"email": AccountInfo.objects.filter(email=newUser["email"]).exists(),
				"phone": AccountInfo.objects.filter(phone=newUser["phone"]).exists(),
			}
			if True in alreadyTaken.values():
				return JsonResponse(alreadyTaken)

			userDemo    = Demographics.objects.create()
			accountInfo = AccountInfo.objects.create(
				email=newUser["email"],
				phone=newUser["phone"],
				preferredLanguage=newUser["preferredLanguage"],

			)
			UserProfile.objects.create(
				userID            = newUser["userID"],
				username          = newUser["username"],
				accountInfo       = accountInfo,
				demographics      = userDemo,
			)

			return HttpResponse(status=201)

		# Deletes the UserProfile entity and related AccountInfo and Demographics entities associated
		# with the recieved userID.
		elif request.method == "DELETE":
			user = UserProfile.objects.get(userID=userID)
			user.delete_user()
			return HttpResponse("Deleted user account")

	except:
		print(" [ERROR]", sys.exc_info()[0])
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
		print(" [ERROR]", sys.exc_info()[0])
		return HttpResponse(status=500)


@csrf_exempt
def following_list(request, userID=None):
	try:
		# Returns a list of all the creators that a user is following.
		if request.method == "GET":	
			user = UserProfile.objects.get(userID=userID)
			return HttpResponse(user.get_followings())

	except:
		print(" [ERROR]", sys.exc_info()[0])
		return HttpResponse(status=500)

@csrf_exempt
def following(request, userID=None, creatorID=None):
	# Handles the one way following relationship between a user and a creator.

	user    = UserProfile.objects.get(userID=userID)
	creator = UserProfile.objects.get(userID=creatorID)

	try:
		# Returns true if the user is currently following the creator, returns false otherwise.
		if request.method == "GET":
			return JsonResponse({"following_bool": (creator in user.get_followings())})

		if request.method == "POST":
			Relationships.objects.create(follower=user, creator=creator)
			return HttpResponse(status=201)	

		if request.method == "DELETE":
			Relationships.objects.get(follower=follower, creator=creator).delete()
			return HttpResponse(status=201)

	except:
		print(" [ERROR]", sys.exc_info()[0])
		return HttpResponse(status=500)


@csrf_exempt
def friends_list(request, userID=None):
	try:
		# Returns a list of all of the user's friends.
		if request.method == "GET":
			friends = UserProfile.objects.get(userID=userID)
			return JsonResponse({'friends' : friends.get_friends()})

	except:
		print(" [ERROR]", sys.exc_info()[0])
		return HttpResponse(status=500)

# @csrf_exempt
# def friends(request, userID=None):
# 	try:

# 		if request.method == "POST":
# 			newFriends  = request.POST
# 			newFriendID = newFriends["newFriendID"]

# 			user      = UserProfile.objects.get(userID=userID)
# 			newFriend = UserProfile.objects.get(userID=newFriendID)

# 			if user.allFriends.filter(userID=newFriend):
# 				return HttpResponse("User is already friends with the other user.")

# 			else:
# 				user.allFriends.add(newFriend)
# 				return HttpResponse("Successfully started a new friendship!")

# 	except:
# 		print(" [ERROR]", sys.exc_info()[0])
# 		return HttpResponse(status=500)

# @csrf_exempt
# def become_friends(request, userID=None):
# 	try:
# 		newFriends  = request.POST
# 		newFriendID = newFriends["newFriendID"]

# 		user      = UserProfile.objects.get(userID=userID)
# 		newFriend = UserProfile.objects.get(userID=newFriendID)

# 		if user.allFriends.filter(userID=newFriend):
# 			return HttpResponse("User is already friends with the other user.")

# 		else:
# 			user.allFriends.add(newFriend)
# 			return HttpResponse("Successfully started a new friendship!")

# 	except:
# 		return HttpResponse(str(sys.exc_info()[0]))

# @csrf_exempt
# def update_friendship(request, userID=None, friendID=None):
# 	try:
# 		if request.method == "DELETE":
# 			user   = UserProfile.objects.get(userID=userID)
# 			friend = UserProfile.objects.get(userID=friendID)

# 			if not user.allFriends.filter(userID=friendID):
# 				return HttpResponse("User is not friends with the other user.")

# 			else:
# 				user.allFriends.remove(friend)
# 				return HttpResponse("Successfully started a new friendship!")

# 	except:
# 		return HttpResponse(str(sys.exc_info()[0]))
