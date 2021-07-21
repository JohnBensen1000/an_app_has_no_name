import datetime
import sys
import json
import os
import smtplib
import ssl

from better_profanity import profanity

from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.apps import apps

from google.cloud import firestore

db = firestore.Client()

User          = apps.get_model("models", "User")
Blocked       = apps.get_model("models", "Blocked")

@csrf_exempt
def comments(request, postID=None):
    try:
        # Recieves a json object with three fields: "comment", "uid", and "path". "comment" contains 
        # the actual comment itself. If the comment contains profanity, returns a json response telling the
        # client that the comment contains profanity. "uid" is the uid of the user who posted the comment. 
        # "path" is the directory of where the new comment will be stored in the firestore database. The 
        # "path" string will be stored in the database so that when someone posts a comment responding to 
        # this comment, the new comment will know where to be placed in the database.    
        
        if request.method == "POST":
            requestJson = json.loads(request.body)

            if profanity.contains_profanity(requestJson["comment"]):
                return JsonResponse({"reasonForDenial": "profanity"}, status=200)

            path          = requestJson["path"] + "/c/" + str(int(datetime.datetime.now().timestamp()))
            commentDocRef = db.document('COMMENTS' + "/%d" % postID + path)

            commentDocRef.set({
                u'datePosted': firestore.SERVER_TIMESTAMP,
                u'uid':        requestJson["uid"],
                u'comment':    requestJson["comment"],
                u'path':       path,
            })
            return JsonResponse({"reasonForDenial": None}, status=201)

        # Gets a list of the comments of a post. 
        if request.method == "GET":
            uid  = request.GET["uid"]
            user = User.objects.get(uid=uid)

            postDoc      = db.collection('COMMENTS').document(str(postID))
            collection   = postDoc.collection("c")
            commentsList = get_all_comments(user, collection, 0)

            return JsonResponse({'comments': commentsList})

    except:
        print(" [ERROR]", sys.exc_info())
        return HttpResponse(status=500)

def get_all_comments(user, collection, level):
    # Comments are stored such that each response comment is stored in a collection 
    # that is under the parent comment. Therefore, this function recursively gets
    # to every comment and creates a list of all comments. Does not return comments
    # from users who deleted their accounts or who the current user is currently blocking.

    allComments = []

    for commentDoc in collection.order_by('datePosted').stream():
        commentDict = commentDoc.to_dict()
        creator     = User.objects.filter(uid=commentDict["uid"]).first()

        if creator is not None and not Blocked.objects.filter(user=user, creator=creator).exists():
            commentDict["level"] = level
            del commentDict["datePosted"]

            subCollection = collection.document(commentDoc.id).collection("c")

            subComments = get_all_comments(user, subCollection, level + 1)
            commentDict['numSubComments'] = len(subComments)
            allComments.append(commentDict)
            if len(subComments) > 0:
                allComments.extend(subComments)

    return allComments

@csrf_exempt
def report(request, postID):
    try:
        if request.method == "POST":
            send_reported_comment_email(postID, json.loads(request.body))
            return HttpResponse(status=201)

    except:
        print(" [ERROR]", sys.exc_info())
        return HttpResponse(status=500)

def send_reported_comment_email(postID, commentJson):
	port    = 465 
	context = ssl.create_default_context()

	with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
		server.login("entropy.developer1@gmail.com", "CominG1$is@Winter6*9sNow11")
		server.sendmail(
			"entropy.developer1@gmail.com", 
			"entropy.developer1@gmail.com", 
			"""
                %s

				Comment: %s
			 	Comment path: %s
				Post ID: %s
			""" % (os.getenv("ENVIRONMENT"), commentJson["comment"], commentJson["path"], postID)
		)