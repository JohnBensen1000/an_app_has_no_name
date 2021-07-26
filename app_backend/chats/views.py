import sys
import json
import os
import ssl
import smtplib
import requests

from better_profanity import profanity

from django.http import HttpResponse, JsonResponse
from django.apps import apps
from django.views.decorators.csrf import csrf_exempt

from google.cloud import firestore
from google.cloud import storage, firestore, vision

from firebase_admin import messaging

serverToken = 'AAAAsEEDk0k:APA91bF1sOQc-E_MFIW9IEDjpELLj3euKlPzAGBfwARrKgX199yD8VrDyx6q5omEkxlzIuK_fU6jb-rAsiRTimhaFtpfq_mXzSZ322PsiMZ65GxFWoIT2lk3ZhwZzJ_Q-MI-E_jMAZo1'

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
        # Returns a list of the chatIDs of each chat that a user is part of. Sorts by the how
        # recent the last chat item was sent in a chat. 
        if request.method == "GET":
            chatIdList = [chatMember.chat.chatID for chatMember in ChatMember.objects.filter(member__uid=uid)]
            chatList   = list()

            for chat in Chat.objects.filter(chatID__in=chatIdList).order_by("-lastChatTime"):
                chatMember            = ChatMember.objects.filter(member__uid=uid).filter(chat__chatID=chat.chatID).first()
                chatDict              = chat.to_dict()
                chatDict['isUpdated'] = chatMember.isUpdated

                chatList.append(chatDict)

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
        # the correct collection). Saves the chat object, forcing it to update it's field "lastChatTime".
        
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
            else:
                if profanity.contains_profanity(newChatJson['text']):
                    return JsonResponse({"reasonForRejection": "profanity"}, status=200)
                docRef.set({
                    'uid':    uid,
                    'time':   firestore.SERVER_TIMESTAMP,
                    'isPost': False,
                    'text':   newChatJson['text']
                })

            chat = Chat.objects.get(chatID=chatID)
            chat.save()

            for chatMember in ChatMember.objects.filter(chat=chat).exclude(member__uid=uid):
                chatMember.isUpdated = False
                chatMember.save()

                if chatMember.member.deviceToken is not None:
                    message = messaging.Message(data={'chatID': chatID}, token=chatMember.member.deviceToken)
                    messaging.send(message)
            
            return JsonResponse({"reasonForRejection": None}, status=201)
            
    except:
        print(" [ERROR]", sys.exc_info())
        return HttpResponse(status=500)

@csrf_exempt
def updated(request, uid=None, chatID=None):
    try:
        # This view exists to let a client tell the database that they have read all the most recent
        # chat items in a particular chat. 
        if request.method == "POST":
            chatMember = ChatMember.objects.filter(chat__chatID=chatID).filter(member__uid=uid).first()
            chatMember.isUpdated = True
            chatMember.save()

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

    except:
        print(" [ERROR]", sys.exc_info())
        return HttpResponse(status=500)

def check_if_post_is_safe(downloadURL):
	image                  = vision.Image()
	image.source.image_uri = downloadURL
	safe                   = visionClient.safe_search_detection(image=image).safe_search_annotation

	for safeAttribute in [safe.adult, safe.medical, safe.spoof, safe.violence, safe.racy]:
		if safeAttribute.value >= 5:
			return False

	return True

def send_firebase_message(user):
    if user.deviceToken is None:
        return

    headers = { 'Content-Type': 'application/json', 'Authorization': 'key=' + serverToken }
    body = {
        'to': user.deviceToken,
        'data': 'testing',
    }

    response = requests.post("https://fcm.googleapis.com/fcm/send", headers=headers, data=json.dumps(body))
    print(response.status_code)
    



    

    


