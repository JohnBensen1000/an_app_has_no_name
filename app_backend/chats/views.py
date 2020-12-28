# export GOOGLE_APPLICATION_CREDENTIALS="/home/john/Downloads/an-app-has-no-name-6a351a8f0853.json"
import sys
import datetime
from google.cloud import firestore, firestore_v1

from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .chats_manager import ChatsManager
 
db           = firestore.Client()
chatsManager = ChatsManager()
chatsManager.start() 

@csrf_exempt
def all_chats(request, userID=None):
	pass

@csrf_exempt
def direct_chat(request, userID=None, recieverID=None):
	try:
		# doc ID is determined by adding userIDs of both users, and the order is determined
		# by which userID is less than the other
		docID  = userID + recieverID if userID < recieverID else recieverID + userID
		docRef = db.collection("Chats").document(docID)
		doc    = docRef.get()

		if request.method == "POST":
			if not doc.exists:
				docRef.set({
					"users":        [userID, recieverID],
					"conversation": list(),
				})

			message = request.POST["message"]
			docRef.update({"conversation": firestore.ArrayUnion([{
				"timeSent": datetime.datetime.now(),
				"message":  message,
			}])})	
			chatsManager.send_message(recieverID, message)

			return HttpResponse(status=200)

		if request.method == "GET":
			return JsonResponse(doc.to_dict())

		if request.method == "DELETE":
			docRef.delete()

	except:
		return HttpResponse(str(sys.exc_info()[1]))


@csrf_exempt
def group_chat(request, userID=None, groupchatID=None):
	pass

@csrf_exempt
def group_member(request, userID=None, groupchatID=None, memberID=None):
	pass
