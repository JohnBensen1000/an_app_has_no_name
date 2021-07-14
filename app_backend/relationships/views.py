import sys
import json
import os
import requests

from django.http import HttpResponse, JsonResponse
from django.apps import apps
from django.views.decorators.csrf import csrf_exempt

from google.cloud import firestore

db = firestore.Client()

serverToken = 'AAAALGfgH5A:APA91bH1FgqgJOZ4LQds7XgnRxatrIxZgP9hzvx8MItG8fsgxDGAgR9XocFWh8qwNfCxBaj-eddA5DwS2r2SNRbNU2iOIJvu-QaXo_2aPf-DujhqdMhz9H3aW5ZItBfXuV0JZ5BGQXDV'

User          = apps.get_model("models", "User")
Preferences   = apps.get_model("models", "Preferences")
Profile       = apps.get_model("models", "Profile")
Following     = apps.get_model("models", "Following")
ChatMember    = apps.get_model("models", "ChatMember")
Chat          = apps.get_model("models", "Chat")
Blocked       = apps.get_model("models", "Blocked")

def create_new_direct_message(user1, user2):
    chat = Chat.objects.create(
        isDirectMessage=True
    )
    
    ChatMember.objects.create(
        isOwner = True,
        chat    = chat,
        member  = user1
    )
    ChatMember.objects.create(
        isOwner = True,
        chat    = chat,
        member  = user2
    )

@csrf_exempt
def followings(request, uid=None):
    try:
        user = User.objects.get(uid=uid)

        # Returns a list of all creators that a user is following. Shows if each creator is a 
        # friend of the user or not. 
        if request.method == "GET":
            followingsList = list()
            for following in Following.objects.filter(follower=user):
                creator = following.creator
                followingsList.append({
                    "user":     creator.to_dict(),
                    "isFriend": Following.objects.filter(follower=creator, creator=user).exists()
                })

            return JsonResponse({"followings": followingsList})

        # Creates a relationship entity that stores the fact that a user is following a creator. The 
        # creator is identified by 'uid' given in the request body. 'newFollower' is a field in 
        # Relationship that keeps track of whether or not to notify a creator that a new user started
        # following them. This will only be set to True if the creator is not already following that 
        # new user. Deletes
        if request.method == "POST":
            requestBody = json.loads(request.body)
            creator     = User.objects.get(uid=requestBody['uid'])
            isNewFriend = Following.objects.filter(follower=creator, creator=user).exists()

            if Blocked.objects.filter(user=user, creator=creator).exists():
                Blocked.objects.filter(user=user, creator=creator).delete()

            Following.objects.create(
                follower    = user,
                creator     = creator,
                newFollower = not isNewFriend, 
            )

            if isNewFriend:
                create_new_direct_message(user, creator)
            else:
                pass
                # send_new_followers(creator)

            return HttpResponse(status=201)	

    except:
        print(" [ERROR]", sys.exc_info())
        return HttpResponse(status=500)

@csrf_exempt
def blocked(request, uid=None):
    try:
        # Creates a blocked relationship between two users. Deletes the following relationship
        # and direct message between the two users if they exist.
        if request.method == "POST":
            requestBody = json.loads(request.body)
            user        = User.objects.get(uid=uid)
            creator     = User.objects.get(uid=requestBody['uid'])  

            if Following.objects.filter(follower=user, creator=creator).exists():
                Following.objects.filter(follower=user, creator=creator).delete()

            Blocked.objects.create(
                user    = user,
                creator = creator,
            )

            delete_direct_messages_if_exists(user, creator)

            return HttpResponse(status=201)

    except:
        print(" [ERROR]", sys.exc_info())
        return HttpResponse(status=500)      

@csrf_exempt
def blocked_user(request, uid=None, creator_uid=None):
    try:
        # Deletes a blocked relationship between two users.
        if request.method == "DELETE":
            user        = User.objects.get(uid=uid)
            creator     = User.objects.get(uid=creator_uid)

            Blocked.objects.filter(user=user, creator=creator).delete()

            return HttpResponse(status=200)

    except:
        print(" [ERROR]", sys.exc_info())
        return HttpResponse(status=500)     

# def send_new_followers(user):
# 	# Sends a push notification to a user with a list of all of their new followers. Sends
# 	# notification through google firebase to a device (identified by userProfile.deviceToken).

#     newFollowers = [relation.follower.to_dict() for relation in Following.objects.filter(newFollower=True, creator=user)]

#     headers = {
#         'Content-Type': 'application/json',
#         'Authorization': 'key=' + serverToken,
#     }
#     body = {
#         'notification': {
#             'body': {"uid": user.uid, "new_followers": newFollowers}
#         },
#         'to': user.deviceToken,
#         'priority': 'high',
#     }
#     response = requests.post("https://fcm.googleapis.com/fcm/send", headers=headers, data=json.dumps(body))


@csrf_exempt
def following(request, uid0=None, uid1=None):
    try:
        follower  = User.objects.get(uid=uid0)
        creator   = User.objects.get(uid=uid1)

        # Checks to see if a user (identified by uid0) is followering another user (identified by uid1)
        if request.method == "GET":
            isFollowing = Following.objects.filter(follower=follower, creator=creator).exists()
            return JsonResponse({"isFollowing": isFollowing})

        # Allows a user to follow back or not follow back a new follower. Either way, the user's new
        # follower will no longer be labeled as a new follower. Returns a 201 status code if the user
        # decides to follow back, returns 200 otherwise. 
        if request.method == "POST":
            following             = Following.objects.get(follower=follower, creator=creator)
            following.newFollower = False
            following.save()

            requestBody = json.loads(request.body)

            if requestBody['followBack']:
                Following.objects.create(
                    follower    = creator,
                    creator     = follower,
                    newFollower = False, 
                )
                create_new_direct_message(follower, creator)

                return HttpResponse(status=201)
            else:
                return HttpResponse(status=200)

        # Deletes a one-way following relationship. If follower is friends with the creator, then
        # deletes the direct message between the two. This includes deleting the chat data in 
        # firestore and the chat entity in the database. 
        if request.method == "DELETE":
            delete_direct_messages_if_exists(follower, creator)

            following = Following.objects.get(follower=follower, creator=creator)
            following.delete()

            return HttpResponse(status=200)

    except:
        print(" [ERROR]", sys.exc_info())
        return HttpResponse(status=500)

@csrf_exempt
def followers(request, uid=None):
    try:
        # Returns a list of all of a user's (identified by uid) followers.
        if request.method == "GET":
            user         = User.objects.get(uid=uid)
            followerList = list() 
            for relationship in Following.objects.filter(creator=user):
                followerList.append(relationship.follower.to_dict())

            return JsonResponse({'followerList': followerList})

    except:
        print(" [ERROR]", sys.exc_info())
        return HttpResponse(status=500)

@csrf_exempt
def new_followers(request, uid=None):
    try:
        # Returns a list of all of a user's (identified by uid) new followers.
        if request.method == "GET":
            user         = User.objects.get(uid=uid)
            followerList = list() 
            for relationship in Following.objects.filter(creator=user, newFollower=True):
                followerList.append(relationship.follower.to_dict())

            return JsonResponse({'followerList': followerList})
    except:
        print(" [ERROR]", sys.exc_info())
        return HttpResponse(status=500)

@csrf_exempt
def friends(request, uid=None):
    try:
        # Returns a list of all a user's friends. A 'friend' is defined as another user that
        # both follows and is followed by a user. 
        if request.method == "GET":
            user        = User.objects.get(uid=uid)
            friendsList = list() 

            for relationship in Following.objects.filter(creator=user):
                follower = relationship.follower
                if Following.objects.filter(creator=follower, follower=user):
                    friendsList.append(follower.to_dict())

            return JsonResponse({'friendsList': friendsList})

    except:
        print(" [ERROR]", sys.exc_info())
        return HttpResponse(status=500)

def delete_direct_messages_if_exists(follower, creator):
    if Following.objects.filter(follower=creator, creator=follower).exists():
        chatDict = dict()

        for chatMember in ChatMember.objects.filter(member=follower):
            if chatMember.chat.isDirectMessage:
                chatDict[chatMember.chat] = True

        for chatMember in ChatMember.objects.filter(member=creator):
            if chatMember.chat in chatDict:
                chat = chatMember.chat

                docRef = db.collection('CHATS').document(chat.chatID)
                colRef = docRef.collection("chats")
                for doc in colRef.stream():
                    doc.reference.delete()

                docRef.delete()
                chat.delete()