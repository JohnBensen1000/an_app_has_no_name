import sys
import json

from django.http import HttpResponse, JsonResponse
from django.apps import apps

User = apps.get_model("models", "User")

def signedInStatus(request, uid=None):
	try:
		# Lets user sign-in/sign-out of their account. If a user signs into their account, the 
		# field "deviceToken" is updated to whatever device the user signed in from. If a user 
		# is signing out of their account, "deviceToken" is set to "" to indicate that the user 
		# is not signed in on any device. 
		if request.method == "POST":
			user        = User.objects.get(uid=uid)
			requestBody = json.loads(request.body)

			if requestBody['signIn'] == True:
				user.deviceToken = requestBody["deviceToken"] 
				user.signedIn    = True

			else:
				user.deviceToken = ""
				user.signedIn    = False

			user.save()

			return HttpResponse(status=200)

	except:
		print(" [ERROR]", sys.exc_info())
		return HttpResponse(status=500)

def deviceSignedInOn(request):
	try:
		# Checks to see if anyone is signed on on a given device (identified by 'deviceToken'). 
		# This is used so that a user doesn't have to sign into their account every time they
		# open the app. 
		if request.method == "GET":
			deviceToken = request.GET["deviceToken"]
			return JsonResponse({
				"signedIn": User.objects.filter(deviceToken=deviceToken).exists()
			})

	except:
		print(" [ERROR]", sys.exc_info())
		return HttpResponse(status=500)
