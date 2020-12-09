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

		if UserProfile.objects.filter(userID=userProfile["userID"]).exists():
			return HttpResponse("A user already has taken this user ID.") 
			#return HttpResponse(UserProfile.objects.filter(userID=userProfile["userID"]))

		demoList = [float(x) for x in userProfile["demographics"].split("[")[1].split("]")[0].split(",")]
		userDemo = Demographics.objects.create()
		userDemo.set_int_list(demoList)

		accountInfo = AccountInfo.objects.create(
			email=userProfile["email"],
    		phone=userProfile["phone"]
		)

		UserProfile.objects.create(
			userID            = userProfile["userID"],
			username          = userProfile["username"],
			preferredLanguage = userProfile["preferredLanguage"],
			demographics      = userDemo,
			accountInfo       = accountInfo
		)
		return HttpResponse("Created new user!")

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
		return HttpResponse(follower.get_followings())

	except:
		return HttpResponse(str(sys.exc_info()[0]))


@csrf_exempt
def get_followers(request):
	try:
		getFollowers = request.GET
		creator      = UserProfile.objects.get(userID=getFollowers["creator"])
		return HttpResponse(creator.get_followers())

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

