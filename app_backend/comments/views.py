# export GOOGLE_APPLICATION_CREDENTIALS="/home/john/Downloads/an-app-has-no-name-6a351a8f0853.json"
# export GOOGLE_APPLICATION_CREDENTIALS="/Users/johnbensen/Downloads/an-app-has-no-name-059c876a8538.json"

import datetime
import sys
from google.cloud import firestore, firestore_v1

from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt

db = firestore.Client()
print("Connected to Firestore.")

@csrf_exempt
def post_comment(request, postID=None, userID=None):
    try:
        if request.method == "POST":
            newComment = request.POST
            path = newComment["path"] + "/c"

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
            return HttpResponse("Successfully posted comment.")

        else:
            return HttpResponse("This request method is currently not supported by this view.")

    except:
        return HttpResponse(str(sys.exc_info()[1]))


def get_sub_comments(collection):
    allComments = []

    for commentDoc in collection.order_by('datePosted').stream():
        commentDict   = commentDoc.to_dict()
        subCollection = collection.document(commentDoc.id).collection("c")

        commentDict["subComments"] = get_sub_comments(subCollection)
        allComments.append(commentDict)

    return allComments

def delete_doc_and_sub_collections(doc):
    for commentDoc in doc.collection('c').stream():
        delete_doc_and_sub_collections(doc.collection('c').document(commentDoc.id))

    doc.delete()

@csrf_exempt
def access_comment(request, postID=None):
    try:
        if request.method == "GET":
            postDoc    = db.collection('Comments').document(str(postID))
            collection = postDoc.collection("c")
            response   = {"comments": get_sub_comments(collection)}

            return JsonResponse(response)

        if request.method == "DELETE":
            postDoc = db.collection('Comments').document(str(postID))
            delete_doc_and_sub_collections(postDoc)

            return HttpResponse(status=204)

    except:
        return HttpResponse(str(sys.exc_info()))



    