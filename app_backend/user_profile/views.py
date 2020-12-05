import sys, json

from django.shortcuts import render
from demographics.models import Demographics
from user_profile.models import *
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt


#@require_http_methods(["POST"])
@csrf_exempt
def create_new_user(request):
	try:
		userProfile = request.POST

		demoList = [float(x) for x in userProfile["demographics"].split("[")[1].split("]")[0].split(",")]
		userDemo = Demographics.objects.create()
		userDemo.set_int_list(demoList)

		usersWithID = UserProfile.objects.filter(userID=userProfile["userID"])

		if usersWithID != []:
			UserProfile.objects.create(
				demographics      = userDemo,
				userID            = userProfile["userID"],
				preferredLanguage = userProfile["preferredLanguage"],
				username          = userProfile["username"]
			)
			return HttpResponse("Created new user!")

		else:
			return HttpResponse("A user already has taken this user ID.")

	except:
		return HttpResponse(str(sys.exc_info()[0]))


@csrf_exempt
def search_creators(request):
	try:
		search = request.GET

		searchString = search["searchString"]

		objectList  = UserProfile.objects.filter(username__icontains=searchString)
		creatorList = [{"username":user.username, "userID":user.userID} for user in objectList]

		if creatorList == []:
			return HttpResponse(None)
		else:
			return HttpResponse(creatorList)

	except:
		return HttpResponse(str(sys.exc_info()[0]))


@csrf_exempt
# TODO? Probably should add an option to 'block' a creator in this field
def start_following(request):
	try:
		following = request.POST

		follower = UserProfile.objects.get(userID=following["follower"])
		creator  = UserProfile.objects.get(userID=following["creator"])

		_, created = Relationships.objects.get_or_create(follower=follower, creator=creator)

		if created:
			return HttpResponse("Successfully started following new creator!")
		else:
			return HttpResponse("User is already following this creator.")

	except:
		return HttpResponse(str(sys.exc_info()[0]))


@csrf_exempt
def get_followings(request):
	try:
		getFollowings = request.GET
		follower      = UserProfile.objects.get(userID=getFollowings["follower"])
		return HttpResponse(follower.get_all_followings(Relationships.following))

	except:
		return HttpResponse(str(sys.exc_info()[0]))


@csrf_exempt
def become_friends(request):
	try:
		friends  = request.POST
		friend_1 = UserProfile.objects.get(userID=friends["friend_1"])
		friend_2 = UserProfile.objects.get(userID=friends["friend_2"])

		friend_1.allFriends.add(friend_2)

		return HttpResponse("Successfully created a new friendship!")

	except:
		return HttpResponse(str(sys.exc_info()[0]))

@csrf_exempt
def get_friends(request):
	try:
		getFriends = request.GET
		friends    = UserProfile.objects.get(userID=getFriends["user"])
		return HttpResponse(friends.get_friends())

	except:
		return HttpResponse(str(sys.exc_info()[0]))

if __name__ == "__main__":
	pass

