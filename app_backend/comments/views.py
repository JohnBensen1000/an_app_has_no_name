# export GOOGLE_APPLICATION_CREDENTIALS="/home/john/Downloads/an-app-has-no-name-6a351a8f0853.json"
# export GOOGLE_APPLICATION_CREDENTIALS="an-app-has-no-name-059c876a8538.json"

import datetime
import sys
from google.cloud import firestore, firestore_v1

from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt

db = firestore.Client()

@csrf_exempt
def comments(request, postID=None):
    try:
        # Recieves a json object with three fields: "comment", "userID", and "path". "comment" contains 
        # the actual comment itself. "userID" is the userID of the user who posted the comment. "path" 
        # is the directory of where the new comment will be stored in the firestore database. The "path"
        # string will be stored in the database so that when someone posts a comment responding to this 
        # comment, the new comment will know where to be placed in the database.    
        if request.method == "POST":
            newComment = request.POST
            userID     = newComment["userID"]
            path       = newComment["path"] + "/c"

            collectionRef = db.collection("Comments/%d" % postID + path)
            userComments  = collectionRef.where('userID', '==', userID).get()

            path         += "/" + userID + str(len(userComments))
            commentDocRef = db.document("Comments/%d" % postID + path)

            commentDocRef.set({
                u'datePosted': firestore.SERVER_TIMESTAMP,
                u'userID': userID,
                u'comment': newComment["comment"],
                u'path': path,
            })
            return HttpResponse(status=201)

        # Gets a list of the comments of a post. 
        if request.method == "GET":
            postDoc      = db.collection('Comments').document(str(postID))
            collection   = postDoc.collection("c")
            commentsList = get_all_comments(collection, 0)

            return JsonResponse({'comments': commentsList})

    except:
        print(" [ERROR]", sys.exc_info())
        return HttpResponse(status=500)

def get_all_comments(collection, level):
    # Comments are stored such that each response comment is stored in a collection 
    # that is under the parent comment. Therefore, this function recursively gets
    # to every comment and creates a list of all comments.

    allComments = []

    for commentDoc in collection.order_by('datePosted').stream():
        commentDict          = commentDoc.to_dict()
        commentDict["level"] = level
        del commentDict["datePosted"]

        subCollection = collection.document(commentDoc.id).collection("c")

        allComments.append(commentDict)
        allComments += get_all_comments(subCollection, level + 1)

    return allComments