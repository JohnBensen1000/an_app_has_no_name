import sys
import json
import os

from django.http import HttpResponse, JsonResponse
from django.apps import apps
from django.views.decorators.csrf import csrf_exempt

import firebase_admin

default_app = firebase_admin.initialize_app()

User        = apps.get_model("models", "User")
Preferences = apps.get_model("models", "Preferences")
Profile     = apps.get_model("models", "Profile")
Post        = apps.get_model("models", "Post")
Following   = apps.get_model("models", "Following")
WatchedBy   = apps.get_model("models", "WatchedBy")
Blocked     = apps.get_model("models", "Blocked")
Reported    = apps.get_model("models", "Reported")
Chat        = apps.get_model("models", "Chat")
ChatMember  = apps.get_model("models", "ChatMember")

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