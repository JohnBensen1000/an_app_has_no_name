
import sys
import json
import os

from django.http import HttpResponse, JsonResponse
from django.apps import apps
from django.views.decorators.csrf import csrf_exempt

import firebase_admin

# default_app = firebase_admin.initialize_app()

User        = apps.get_model("models", "User")
Preferences = apps.get_model("models", "Preferences")
Profile     = apps.get_model("models", "Profile")
Blocked     = apps.get_model("models", "Blocked")
ChatMember  = apps.get_model("models", "ChatMember")
Chat        = apps.get_model("models", "Chat")


@csrf_exempt
def users(request):
	try:
		# Recieves a json object containing fields that correspond to a new user's account. First checks to
		# see if any unique fields (userID, email, and phone) have been taken by another user. If any of these
		# fields have been taken, returns a list of the taken fields. If not, then creates a new User entity. 
		if request.method == "POST":			
			newUser = json.loads(request.body)

			if User.objects.filter(userID=newUser["userID"]):
				return JsonResponse({"denied": "userIdTaken"})
                
			else:
				user = User.objects.create(
					userID      = newUser["userID"],
					email       = newUser['email'],
					uid         = newUser["uid"],
					username    = newUser["username"],
					preferences = Preferences.objects.create(),
					profile     = Profile.objects.create(),
				)

				return JsonResponse(user.to_dict())

		# Recieves a string and returns a list of all users whose userID contains the string. If a value
		# for "uid" is given as a parameter, then this view doesn't return any users blocked by the user
		# identified by the given uid. 
		if request.method == "GET":
			searchString = request.GET["contains"]
			uid          = request.GET["uid"] if "uid" in request.GET else None

			if searchString == '':
				return JsonResponse({"creatorsList": []})

			objectList   = User.objects.filter(userID__icontains=searchString)
			creatorsList = list()
			blockedList  = [blocked.creator for blocked in Blocked.objects.filter(user__uid=uid)]

			for creator in objectList:
				if creator not in blockedList and creator.uid != uid:
					creatorsList.append(creator.to_dict())

			return JsonResponse({"creatorsList": creatorsList})

	except:
		print(" [ERROR]", sys.exc_info())
		return HttpResponse(status=500)

@csrf_exempt
def user(request, uid=None):
	try:
		# Recieves the uid for a user, and returns information about that user.
		if request.method == "GET":
			return JsonResponse(User.objects.get(uid=uid).to_dict())

		# Allows a user to update some of the fields of their account.
		if request.method == "PUT":
			user 	= User.objects.get(uid=uid)
			newData = json.loads(request.body)

			if 'profileColor' in newData:
				user.profileColor = newData['profileColor'] 
			if 'username' in newData:
				user.username = newData['username']
			if 'deviceToken' in newData:
				user.deviceToken = newData['deviceToken']
			user.save()

			return JsonResponse(user.to_dict())

		# When deleting a user account, the Preference and Profile models that are associated with
		# it have to also be deleted. the method, delete_account(), takes care of that. Also makes 
		# sure that every direct message that the user is part of is deleted.
		if request.method == "DELETE":
			user = User.objects.get(uid=uid)

			for chatMember in ChatMember.objects.filter(member=user):
				if chatMember.chat.isDirectMessage:
					chatMember.chat.delete()
				chatMember.delete()

			user.delete()
			
			return JsonResponse({'deleted': True})

	except:
		print(" [ERROR]", sys.exc_info())
		return HttpResponse(status=500)

@csrf_exempt
def activity(request, uid=None):
	try:
		if request.method == "GET":
			user = User.objects.get(uid=uid)
			return JsonResponse({'isUpdated': user.isUpdated})

		if request.method == "PUT":
			user = User.objects.get(uid=uid)
			user.isUpdated = True
			user.save()

			return JsonResponse({'isUpdated': user.isUpdated})

	except:
		print(" [ERROR]", sys.exc_info())
		return HttpResponse(status=500)
