import sys
import json

from django.http import HttpResponse, JsonResponse
from django.apps import apps

User        = apps.get_model("models", "User")
Preferences = apps.get_model("models", "Preferences")
Profile     = apps.get_model("models", "Profile")

def new_user(request):
	try:
		# Recieves a json object containing fields that correspond to a new user's account. First checks to
		# see if any unique fields (userID, email, and phone) have been taken by another user. If any of these
		# fields have been taken, returns a list of the taken fields. If not, then creates a new User entity. 
		if request.method == "POST":
			newUser = json.loads(request.body)

			fieldsTaken = list()
			for uniqueField in ["userID", "email", "phone", "uid"]:
				filter              = {}
				filter[uniqueField] = newUser[uniqueField]

				if User.objects.filter(**filter).exists():
					fieldsTaken.append(uniqueField)

			if len(fieldsTaken) > 0:
				return JsonResponse({"alreadyTaken": fieldsTaken}, status=400)

			else:
				preferences = Preferences.objects.create()
				profile     = Profile.objects.create()

				User.objects.create(
					userID      = newUser["userID"],
					email       = newUser['email'],
					phone       = newUser['phone'],
					deviceToken = newUser["deviceToken"],
					uid         = newUser["uid"],
					username    = newUser["username"],
					preferences = preferences,
					profile     = profile,
				)

				return HttpResponse(status=201)

	except:
		print(" [ERROR]", sys.exc_info())
		return HttpResponse(status=500)

def search(request):
	try:
		# Recieves a string and returns a list of all users whose username contains the string. If 
		# no usernames contain this string, returns an empty list.
		if request.method == "GET":
			searchString = request.GET["contains"]

			if searchString == '':
				return JsonResponse({"creatorsList": []})

			objectList   = User.objects.filter(username__icontains=searchString)
			creatorList  = [{"username":user.username, "userID":user.userID} for user in objectList]

			if creatorList == []:
				return JsonResponse({"creatorsList": []})
			else:
				return JsonResponse({"creatorsList": creatorList})

	except:
		print(" [ERROR]", sys.exc_info())
		return HttpResponse(status=500)

def user(request, uid=None):
	try:
		user = User.objects.get(uid=uid)

		# Recieves the userID for a user, and returns information about that user.
		if request.method == "GET":
			userDict = {
				'userID':   user.userID,
				'username': user.username,
				'email':    user.email,
				'phone':    user.phone,
			}
			return JsonResponse(userDict)

		# Updates a user's account data with the recieved data. If the recieved phone or email
		# have been already been taken by another user, returns a list of taken fields and doesn't
		# update the user's account data.
		if request.method == "POST":
			newData = json.loads(request.body)

			fieldsTaken = list()

			if User.objects.filter(email=newData['email']).exists():
				fieldsTaken.append('email')
			if User.objects.filter(phone=newData['phone']).exists():
				fieldsTaken.append('phone')

			if len(fieldsTaken) > 0:
				return JsonResponse({"alreadyTaken": fieldsTaken}, status=400)
			
			else:
				user.email    = newData['email']
				user.phone    = newData['phone']
				user.username = newData['username']
				user.save()

				return HttpResponse(status=200) 

		# When deleting a user account, the Preference and Profile models that are associated with
		# it have to also be deleted. the method, delete_account(), takes care of that. 
		if request.method == "DELETE":
			user.delete_account()
			return HttpResponse(status=200)
			
	except:
		print(" [ERROR]", sys.exc_info())
		return HttpResponse(status=500)

def profile(request, uid=None):
	# The profile attribute in the AccountInfo field contains information on a user's profile. A user's
	# profile could be an image, video, or non-existent. This information is used to determine whether
	# to create a profile for a user, and if the profile should be in image of video format. 

	try:
		# Gets the profile status of a a user's profile. 
		if request.method == "GET":
			user = User.objects.get(uid=uid)
			return JsonResponse({"profileType": user.accountInfo.profileType})

		# Updated the profile status of a user's profile.
		elif request.method == "POST":
			user = User.objects.get(uid=uid)
			user.accountInfo.profileType = json.loads(request.body)["profileType"]
			user.accountInfo.save()

			return HttpResponse(status=201)

	except:
		print(" [ERROR]", sys.exc_info())
		return HttpResponse(status=500)