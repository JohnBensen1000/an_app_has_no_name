import sys, json

from django.shortcuts import render
from user_profile.models import *
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from graph_data.models import *

config.ENCRYPTED_CONNECTION = False
config.DATABASE_URL = 'bolt://neo4j:PulpFiction1@localhost:7687' # default


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
def create_new_user(request):
	try:
		userProfile = request.POST

		if UserProfile.objects.filter(userID=userProfile["userID"]).exists():
			return HttpResponse("A user already has taken this user ID.") 

		embedding = [float(x) for x in userProfile["embedding"].split("[")[1].split("]")[0].split(",")]
		UserNode(userID=userProfile["userID"], embedding=embedding).save()

		accountInfo = AccountInfo.objects.create(
			email=userProfile["email"],
    		phone=userProfile["phone"]
		)
		UserProfile.objects.create(
			userID            = userProfile["userID"],
			username          = userProfile["username"],
			preferredLanguage = userProfile["preferredLanguage"],
			accountInfo       = accountInfo
		)

		return HttpResponse("Created new user!")

	except:
		return HttpResponse(str(sys.exc_info()[0]))

@csrf_exempt
def update_user(request, userID=None):
	try:
		if request.method == "GET":
			user     = UserProfile.objects.get(userID=userID)
			userJson = user.get_user_info_json()

			return HttpResponse(userJson)

		elif request.method == "DELETE":
			UserNode.nodes.get(userID=userID).delete()
			UserProfile.objects.get(userID=userID).delete()

			return HttpResponse("Deleted user account")

	except:
		return HttpResponse(str(sys.exc_info()[0]))


@csrf_exempt
def get_followings(request, userID=None):
	try:
		follower = UserProfile.objects.get(userID=userID)
		return HttpResponse(follower.get_followings())

	except:
		return HttpResponse(str(sys.exc_info()[0]))

@csrf_exempt
def start_following(request, followerID=None):
	# TODO? Probably should add an option to 'block' a creator in this field
	try:
		following = request.POST

		follower = UserProfile.objects.get(userID=userID)
		creator  = UserProfile.objects.get(userID=following["creatorID"])

		if follower.followings.filter(creator=creator):
			return HttpResponse("User is already following this creator.")

		else:
			followerNode = UserNode.nodes.get(userID=userID)
			creatorNode  = UserNode.nodes.get(userID=following["creatorID"])
			followerNode.following.connect(creatorNode)

			Relationships.objects.create(follower=follower, creator=creator)

			return HttpResponse("Successfully started following new creator!")

	except:
		return HttpResponse(str(sys.exc_info()[0]))

@csrf_exempt
def update_following(request, userID=None, creatorID=None):
	try:
		if request.method == "DELETE":
			follower = UserProfile.objects.get(userID=userID)
			creator  = UserProfile.objects.get(userID=creatorID)

			if not follower.followings.filter(creator=creator):
				return HttpResponse("User is not following this creator.")

			else:
				followerNode = UserNode.nodes.get(userID=userID)
				creatorNode  = UserNode.nodes.get(userID=creatorID)
				followerNode.following.disconnect(creatorNode)

				Relationships.objects.get(follower=follower, creator=creator).delete()

				return HttpResponse("Successfully deleted the following relation.")

		else:
			return HttpResponse("Request method is not supported for this function.")

	except:
		return HttpResponse(str(sys.exc_info()[0]))


@csrf_exempt
def get_friends(request, userID=None):
	try:
		friends = UserProfile.objects.get(userID=userID)
		return HttpResponse(friends.get_friends())

	except:
		return HttpResponse(str(sys.exc_info()[0]))

@csrf_exempt
def become_friends(request, userID=None):
	try:
		newFriends  = request.POST
		newFriendID = newFriends["newFriendID"]

		user      = UserProfile.objects.get(userID=userID)
		newFriend = UserProfile.objects.get(userID=newFriendID)

		if user.allFriends.filter(userID=newFriend):
			return HttpResponse("User is already friends with the other user.")

		else:
			userNode      = UserNode.nodes.get(userID=userID)
			newFriendNode = UserNode.nodes.get(userID=newFriendID)
			userNode.friends.connect(newFriendNode)

			user.allFriends.add(newFriend)

			return HttpResponse("Successfully started a new friendship!")

	except:
		return HttpResponse(str(sys.exc_info()[0]))

@csrf_exempt
def update_friendship(request, userID=None, friendID=None):
	try:
		if request.method == "DELETE":
			user   = UserProfile.objects.get(userID=userID)
			friend = UserProfile.objects.get(userID=friendID)

			if not user.allFriends.filter(userID=friendID):
				return HttpResponse("User is not friends with the other user.")

			else:
				userNode      = UserNode.nodes.get(userID=userID)
				newFriendNode = UserNode.nodes.get(userID=friendID)
				userNode.friends.disconnect(newFriendNode)

				user.allFriends.remove(friend)

				return HttpResponse("Successfully started a new friendship!")

	except:
		return HttpResponse(str(sys.exc_info()[0]))



if __name__ == "__main__":
	pass

