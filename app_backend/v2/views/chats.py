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

import methods.nsfw_filter as nsfw_filter

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
        # Allows a user to create a new chat. The user is able to decide if the chat is a direct message 
        # or not. The user is able to add members to the chat by adding a list of users to the "members" 
        # field. For direct messages, there will only be one other user in this list, and that user will 
        # also be the 'owner' of the  chat. Also, the user is not able to set a chat name for direct
        # messages.
        if request.method == "POST":
            user        = User.objects.get(uid=uid)
            requestJson = json.loads(request.body)

            if requestJson['isDirectMessage']: chatName = ''
            else:                              chatName = requestJson['chatName']

            chat = Chat.objects.create(
                chatName        = chatName,
                isDirectMessage = requestJson['isDirectMessage']
            )

            ChatMember.objects.create(
                member          = user,
                chat            = chat,
                isOwner         = True,
            )
            for uid in requestJson['members']:
                ChatMember.objects.create(
                    member   = User.objects.get(uid=uid),
                    chat     = chat,
                    isOwner  = requestJson['isDirectMessage'],
                )

            return JsonResponse(chat.to_dict())

        # Returns a list of the chatIDs of each chat that a user is part of. 
        if request.method == "GET":
            user     = User.objects.get(uid=uid)
            chatList = list()
            for chatMember in ChatMember.objects.filter(member=user):
                chatList.append(chatMember.chat.to_dict())

            return JsonResponse({"chats": chatList})

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
                if not nsfw_filter.check_if_post_is_safe(newChatJson['downloadURL']):
                    return JsonResponse({"denied": "NSFW"})

                chatItem = {
                    'uid':    uid,
                    'time':   firestore.SERVER_TIMESTAMP,
                    'isPost': True,
                    'post':   {
                        'downloadURL': newChatJson['downloadURL'],
                        'isImage':     newChatJson['isImage']
                    }
                }
                docRef.set(chatItem)

                return JsonResponse(chatItem)

            else:
                if profanity.contains_profanity(newChatJson['text']):
                    return JsonResponse({"denied": "profanity"})

                chatItem = {
                    'uid':    uid,
                    'time':   firestore.SERVER_TIMESTAMP,
                    'isPost': False,
                    'text':   newChatJson['text']
                } 
                docRef.set(chatItem)

            return JsonResponse(chatItem)
            
    except:
        print(" [ERROR]", sys.exc_info())
        return HttpResponse(status=500)