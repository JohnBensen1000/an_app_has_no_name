import sys

from django.shortcuts import render
from demographics.models import Demographics
from user_profile.models import UserProfile
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt


#@require_http_methods(["POST"])
@csrf_exempt
def create_new_user(request):
	try:
		userProfile = request.POST

		userDemo = Demographics()
		demoList = [float(x) for x in userProfile["demographics"].split("[")[1].split("]")[0].split(",")]
		userDemo.set_int_list(demoList)
		userDemo.save()

		newUser = UserProfile(
			demographics=userDemo,
			userID=userProfile["userID"],
			preferredLanguage=userProfile["preferredLanguage"],
			username=userProfile["username"]
			)
		newUser.save()

		return HttpResponse(("Created a new account for user: " + newUser.username))

	except:
		return HttpResponse(str(sys.exc_info()[0]))

	# graph.create_user_node(request["userID"])

	# print(" [a] Created a new user account for user: ", request["userID"], "who chose the username: ", request["username"])


