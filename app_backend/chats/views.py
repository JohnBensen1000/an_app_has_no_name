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
	try:
		chatsRef = db.collection("Chats")
		docs = chatsRef.where('members', 'array_contains', userID).order_by(
    		'lastUpdated', direction=firestore.Query.DESCENDING).stream()

		chatsDict = {"chats": list()}

		for doc in docs:
			chatsDict["chats"].append({
				"chatID":   doc.id,
				"chatInfo": doc.to_dict()
			})

		return JsonResponse(chatsDict)

	except:
		return HttpResponse(str(sys.exc_info()))


@csrf_exempt
def new_group_chat(request, userID=None):
	try:
		newGroupChat = request.POST
		docRef       = db.collection("Chats").document(newGroupChat["groupchatID"])
		docRef.set({
			"members":      [userID],
			"chatType":     "group",
			"lastUpdated":	datetime.datetime.now()
		})
		convRef = docRef.collection("conversations").document(str(1))
		convRef.set({"conversation": list()})

		return HttpResponse(status=201)

	except:
		return HttpResponse(str(sys.exc_info()))

@csrf_exempt
def new_direct_chat(request, userID=None):
	try:
		recieverID = request.POST["recieverID"]
		# doc ID is determined by adding userIDs of both users, and the order is determined
		# by which userID is less than the other
		docID  = userID + recieverID if userID < recieverID else recieverID + userID
		docRef = db.collection("Chats").document(docID)

		if not docRef.get().exists:
			docRef.set({
				"members":      [userID, recieverID],
				"chatType": 	"direct",
				"lastUpdated":	datetime.datetime.now()
			})
			convRef = docRef.collection("conversations").document(str(1))
			convRef.set({"conversation": list()})

			return HttpResponse(status=201)

		else:
			return HttpResponse(status=200)

	except:
		return HttpResponse(str(sys.exc_info()))


@csrf_exempt
def chat(request, userID=None, chatID=None):
	# same function for direct and group chats, recieverID could be a user or a group
	try:
		if request.method == "POST":
			message = request.POST["message"]
			docRef  = db.collection("Chats").document(chatID)
			doc     = docRef.get()
			convRef = docRef.collection("conversations").document(str(1))

			docRef.update({"lastUpdated": datetime.datetime.now()})

			convRef.update({"conversation": firestore.ArrayUnion([{
				"timeSent": datetime.datetime.now(),
				"message":  message,
				"sender":   userID,
				"Post":     False,
			}])})	

			for recieverID in doc.to_dict()["members"]:
				if recieverID is not userID:
					chatsManager.send_message(chatID, recieverID, message)

		return HttpResponse(status=200)

		if request.method == "GET":
			return JsonResponse(doc.to_dict())

	except:
		return HttpResponse(str(sys.exc_info()))


@csrf_exempt
def group_member(request, userID=None, chatID=None, memberID=None):
	try:
		docRef  = db.collection("Chats").document(chatID)
		doc     = docRef.get()
		docDict = doc.to_dict()

		if docDict["chatType"] == "direct":
			return HttpResponse("You cannot add or remove members to/from a direct chat.")

		if request.method == "POST":
			docRef.update({"members": firestore.ArrayUnion([memberID])})
			return HttpResponse(status=201)

		if request.method == "DELETE":
			docRef.update({"members": firestore.ArratRemove([memberID])})
			return HttpResponse(status=200)

	except:
		return HttpResponse(str(sys.exc_info()))

