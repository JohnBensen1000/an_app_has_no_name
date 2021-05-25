import sys
import json

from django.http import HttpResponse, JsonResponse
from django.apps import apps
from django.forms.models import model_to_dict

User        = apps.get_model("models", "User")
Preferences = apps.get_model("models", "Preferences")
Profile     = apps.get_model("models", "Profile")

def new_user(request):
	try:
		# Recieves a json object containing fields that correspond to a new user's account. First checks to
		# see if any unique fields (userID, email, and phone) have been taken by another user. If any of these
		# fields have been taken, returns a list of the taken fields. If not, then creates a new User entity. 
		if request.method == "POST":
			newUser = request.POST

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

def user(request, userID=None):
	try:
		user = User.objects.get(userID=userID)

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
			newData = request.POST

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

def profile(request):
    pass