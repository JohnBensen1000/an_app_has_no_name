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
def preferences(request):
	try:
		# Simply returns a list of all fields found in the Preferences class. 
		if request.method == "GET":
			return JsonResponse({"fields": Preferences().fields})

	except:
		print(" [ERROR]", sys.exc_info())
		return HttpResponse(status=500)

@csrf_exempt
def user_preferences(request, uid=None):
	try:
		# Returns a list of all of the user's preferences. 
		if request.method == "GET":
			return JsonResponse(User.objects.get(uid=uid).preferences.to_dict())

		# Recieves a list of preference field names. If that field has a value less than .9, sets
		# it's value to .9.
		if request.method == "PUT":
			user           = User.objects.get(uid=uid)
			newPreferences = json.loads(request.body)

			for preference in newPreferences['preferences']:
				if user.preferences.__dict__[preference] < .9:
					user.preferences.__dict__[preference] = .9

			user.preferences.save()

			return JsonResponse(user.preferences.to_dict())

	except:
		print(" [ERROR]", sys.exc_info())
		return HttpResponse(status=500)	