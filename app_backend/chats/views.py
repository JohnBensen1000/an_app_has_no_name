import sys
import json
import os
import ssl
import smtplib

from better_profanity import profanity

from django.http import HttpResponse, JsonResponse
from django.apps import apps
from django.views.decorators.csrf import csrf_exempt

from google.cloud import firestore
from google.cloud import storage, firestore, vision

db = firestore.Client()

User          = apps.get_model("models", "User")
Preferences   = apps.get_model("models", "Preferences")
Profile       = apps.get_model("models", "Profile")
ChatMember    = apps.get_model("models", "ChatMember")
Chat          = apps.get_model("models", "Chat")

client = storage.Client(project=os.getenv("CLIENT"))
bucket = client.get_bucket(os.getenv("BUCKET"))

visionClient = vision.ImageAnnotatorClient()

@csrf_exempt
def chats(request, uid=None):
    try:
        user = User.objects.get(uid=uid)

        # Returns a list of the chatIDs of each chat that a user is part of. 
        if request.method == "GET":
            chatList = list()
            for chatMember in ChatMember.objects.filter(member=user):
                chatList.append(chatMember.chat.to_dict())

            return JsonResponse({"chats": chatList})

        # Allows a user to create a new chat. The user who creates the chat automatically set
        # as a member of the chat. 
        if request.method == "POST":
            chat = Chat.objects.create(
                chatName=json.loads(request.body)['chatName']
            )
            ChatMember.objects.create(
                member  = user,
                chat    = chat,
                isOwner = True,
            )

            return HttpResponse(status=201)

    except:
        print(" [ERROR]", sys.exc_info())
        return HttpResponse(status=500)

@csrf_exempt
def chat(request, uid=None, chatID=None):
    try:
        # Handles posting a new chat. A new chat could be a text or a post (image/video). If the new chat is
        # a post, then checks if the post is NSFW. If it isn't, saves the post in the appropriate location in 
        # google storage. Then creates a new document in google firestore (in the correct collection), 
        # documenting the sender and location of the post. If the new chat is a text, then checks if it contains
        # profanity. If it doesn't, then stores the chat and sender in a new document in google firestore (in 
        # the correct collection).
        if request.method == "POST":
            newChatJson = json.loads(request.body)

            docRef = db.collection('CHATS').document(chatID).collection("chats").document()

            if newChatJson['isPost']:
                if not check_if_post_is_safe(newChatJson['downloadURL']):
                    return JsonResponse({"reasonForRejection": "NSFW"}, status=200)

                docRef.set({
                    'uid':    uid,
                    'time':   firestore.SERVER_TIMESTAMP,
                    'isPost': True,
                    'post':   {
                        'downloadURL': newChatJson['downloadURL'],
                        'isImage':     newChatJson['isImage']
                    }
                })

                return JsonResponse({"reasonForRejection": None}, status=201)

            else:
                if profanity.contains_profanity(newChatJson['text']):
                    return JsonResponse({"reasonForRejection": "profanity"}, status=200)
                    
                docRef.set({
                    'uid':    uid,
                    'time':   firestore.SERVER_TIMESTAMP,
                    'isPost': False,
                    'text':   newChatJson['text']
                })

            return JsonResponse({"reasonForRejection": None}, status=201)
            
        # Allows a user to leave a chat. If the chat is a direct message, then deletes the chat. Otherwise,
        # deletes the ChatMember entity that shows that a user is in a chat.  
        if request.method == "DELETE":
            chat = Chat.objects.get(chatID=chatID)
            user = User.objects.get(uid=uid)

            if chat.isDirectMessage:
                docRef = db.collection('CHATS').document(chatID)
                colRef = docRef.collection("chats")
                for doc in colRef.stream():
                    doc.reference.delete()

                docRef.delete()
                chat.delete()

            else:
                ChatMember.objects.get(member=user, chat=chat).delete()

            return HttpResponse(status=200)
            
    except:
        print(" [ERROR]", sys.exc_info())
        return HttpResponse(status=500)

@csrf_exempt
def report(request, uid=None, chatID=None):
    try:
        # When a user reports a chat item, sends an email to the development account with the
        # json object containing the chat item, the chat ID, and the uid of the user who reported 
        # the chat item. 
        if request.method == "POST":
            chat        = Chat.objects.get(chatID=chatID)
            user        = User.objects.get(uid=uid)
            requestBody = json.loads(request.body)

            port    = 465 
            context = ssl.create_default_context()

            with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
                server.login("entropy.developer1@gmail.com", "CominG1$is@Winter6*9sNow11")
                server.sendmail(
                    "entropy.developer1@gmail.com", 
                    "entropy.developer1@gmail.com", 
                    """
                        %s

                        Chat item: %s
                        Chat: %s
                        Reporting user uid: %s
                    """ % (os.getenv("ENVIRONMENT"), json.dumps(requestBody["chatItem"]), chat.chatID, user.uid)
                )

            return HttpResponse(status=200)

    except:
        print(" [ERROR]", sys.exc_info())
        return HttpResponse(status=500)

@csrf_exempt
def members(request, uid=None, chatID=None):
    try:
        chat = Chat.objects.get(chatID=chatID)

        # Returns a list of all members in a chat. 
        if request.method == "GET":
            membersList = list()
            for chatMember in ChatMember.objects.filter(chat=chat):
                membersList.append(chatMember.member.to_dict())

            return JsonResponse({
                'membersList': membersList
            })

        # Allows a user to add a member to a chat.
        if request.method == "POST":
            requestJson = json.loads(request.body)
            newMember   = User.objects.get(uid=requestJson['uid'])

            ChatMember.objects.create(
                chat    = chat,
                isOwner = False,
                member  = newMember
            )
            return HttpResponse(status=201)

        # Allows a user to remove a user from a chat. 
        if request.method == "DELETE":
            requestJson = json.loads(request.body)
            chatMember  = User.objects.get(uid=requestJson['uid'])

            ChatMember.objects.get(member=chatMember, chat=chat).delete()

            return HttpResponse(status=200)

    except:
        print(" [ERROR]", sys.exc_info())
        return HttpResponse(status=500)

def check_if_post_is_safe(downloadURL):
	image                  = vision.Image()
	image.source.image_uri = downloadURL
	safe                   = visionClient.safe_search_detection(image=image).safe_search_annotation

	for safeAttribute in [safe.adult, safe.medical, safe.spoof, safe.violence, safe.racy]:
		if safeAttribute.value >= 4:
			return False

	return True


