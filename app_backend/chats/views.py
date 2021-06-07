import sys
import json
import random
import datetime
import os

from django.http import HttpResponse, JsonResponse
from django.apps import apps
from django.views.decorators.csrf import csrf_exempt

from google.cloud import firestore
from google.cloud import storage, firestore

db = firestore.Client()

User          = apps.get_model("models", "User")
Preferences   = apps.get_model("models", "Preferences")
Profile       = apps.get_model("models", "Profile")
Relationships = apps.get_model("models", "Relationships")
ChatMember    = apps.get_model("models", "ChatMember")
Chat          = apps.get_model("models", "Chat")

client = storage.Client(project="an-app-has-no-name")
bucket = client.get_bucket("an-app-has-no-name.appspot.com")

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
        # a post, then saves the post in the appropriate location in google storage. Then creates a new document
        # in google firestore (in the correct collection), documenting the sender and location of the post. If 
        # the new chat is a text, then stores the chat and sender in a new document in google firestore (in the
        # correct collection).
        if request.method == "POST":
            if 'json' in request.POST: newChatJson = json.loads(request.POST['json'])  
            else:                      newChatJson = json.loads(request.body)

            docRef = db.collection(os.environ["CHAT_COLLECTION_NAME"]).document(chatID).collection("chats").document()

            if newChatJson['isPost']:
                fileName  = str(int(100 * datetime.datetime.now().timestamp()))
                directory = os.environ["STORAGE_DIR"]

                if newChatJson['isImage']:
                    blob = bucket.blob("%s/%s/%s.png" % (directory, chatID, fileName))
                    blob.content_type = "image/png"
                else:
                    blob = bucket.blob("%s/%s/%s.mp4" % (directory, chatID, fileName))
                    blob.content_type = "video/mp4"

                blob.upload_from_file(request.FILES['media'])
                blob.make_public()
            
                docRef.set({
                    'uid':    uid,
                    'time':   firestore.SERVER_TIMESTAMP,
                    'isPost': True,
                    'post':   {
                        'downloadURL': blob.public_url,
                        'isImage':     newChatJson['isImage']
                    }
                })

            else:
                docRef.set({
                    'uid':    uid,
                    'time':   firestore.SERVER_TIMESTAMP,
                    'isPost': False,
                    'text':   newChatJson['text']
                })

            return HttpResponse(status=201)
            
        # Allows a user to leave a chat. If the chat is a direct message, then deletes the chat. Otherwise,
        # deletes the ChatMember entity that shows that a user is in a chat.  
        if request.method == "DELETE":
            chat = Chat.objects.get(chatID=chatID)
            user = User.objects.get(uid=uid)

            if chat.isDirectMessage:
                docRef = db.collection(os.environ["CHAT_COLLECTION_NAME"]).document(chatID)
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