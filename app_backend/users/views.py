import sys
import json

from django.http import HttpResponse, JsonResponse
from django.apps import apps
from django.views.decorators.csrf import csrf_exempt

User        = apps.get_model("models", "User")
Preferences = apps.get_model("models", "Preferences")
Profile     = apps.get_model("models", "Profile")

@csrf_exempt
def search(request):
	try:
		# Recieves a string and returns a list of all users whose username contains the string. If 
		# no usernames contain this string, returns an empty list.
		if request.method == "GET":
			searchString = request.GET["contains"]

			if searchString == '':
				return JsonResponse({"creatorsList": []})

			objectList   = User.objects.filter(username__icontains=searchString)
			creatorList  = [user.to_dict() for user in objectList]

			if creatorList == []:
				return JsonResponse({"creatorsList": []})
			else:
				return JsonResponse({"creatorsList": creatorList})

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
			newUser = json.loads(request.body)

			fieldsTaken = list()
			for uniqueField in ["userID", "email", "phone", "uid"]:
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
					phone       = newUser['phone'],
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
			user.delete_account()
			return HttpResponse(status=200)
			
	except:
		print(" [ERROR]", sys.exc_info())
		return HttpResponse(status=500)

