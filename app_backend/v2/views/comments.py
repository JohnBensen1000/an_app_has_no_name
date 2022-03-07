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

import methods.activity_feed as activity_feed
import methods.firestore_helpers as firestore_helpers

db = firestore.Client()

User          = apps.get_model("models", "User")
Blocked       = apps.get_model("models", "Blocked")
Post          = apps.get_model("models", "Post")

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
            post        = Post.objects.get(postID=postID)

            if profanity.contains_profanity(requestJson["comment"]):
                return JsonResponse({"denied": "profanity"})

            if requestJson["uid"] in [None, ""]:
                return JsonResponse({'denied': 'invalid/empty uid'})

            path          = requestJson["path"] + "/c/" + str(int(datetime.datetime.now().timestamp()))
            commentDocRef = db.document('COMMENTS' + "/%s" % postID + path)

            commentDict = {
                'datePosted': firestore.SERVER_TIMESTAMP,
                'uid':        requestJson["uid"],
                'comment':    requestJson["comment"],
                'path':       path,
            }
            commentDocRef.set(commentDict)

            if post.creator.uid != requestJson["uid"]:
                activity_feed.add_new_comment(postID, requestJson["uid"])

            del commentDict["datePosted"]

            return JsonResponse(commentDict)

        # Gets a list of the comments of a post. 
        if request.method == "GET":
            uid  = request.GET["uid"]
            user = User.objects.get(uid=uid)

            postDoc      = db.collection('COMMENTS').document(str(postID))
            collection   = postDoc.collection("c")
            commentsList = get_all_comments(user, collection, 0)

            return JsonResponse({'comments': commentsList})

        if request.method == "DELETE":
            body          = json.loads(request.body)
            commentDocRef = db.document('COMMENTS/' + postID + body["path"])
            firestore_helpers.delete_document_and_sub_collections(commentDocRef)
            
            return JsonResponse({})

    except:
        print(" [ERROR]", sys.exc_info())
        return HttpResponse(status=500)

def get_all_comments(user, collection, level):
    # Comments are stored such that each response comment is stored in a collection 
    # that is under the parent comment. Therefore, this function recursively gets
    # to every comment and creates a list of all comments.

    allComments = []

    for commentDoc in collection.order_by('datePosted').stream():
        commentDict = commentDoc.to_dict()
        creator     = None

        if commentDict["uid"] is not None:
            creator = User.objects.get(uid=commentDict["uid"])

        if creator == None or not Blocked.objects.filter(user=user, creator=creator).exists():
            commentDict["level"] = level
            del commentDict["datePosted"]

            subCollection = collection.document(commentDoc.id).collection("c")

            subComments = get_all_comments(user, subCollection, level + 1)
            commentDict['numSubComments'] = len(subComments)
            allComments.append(commentDict)
            if len(subComments) > 0:
                allComments.extend(subComments)

    return allComments