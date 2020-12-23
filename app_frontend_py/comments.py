# export GOOGLE_APPLICATION_CREDENTIALS="/home/john/Downloads/an-app-has-no-name-6a351a8f0853.json"
import datetime
from google.cloud import firestore, firestore_v1

# Add a new document
db = firestore.Client()
print("Connected to Firestore.")

def post_comment(userID, postID, path, comment):
    path = "Comments/%d%s/c" % (postID, path)

    collectionRef = db.collection(path)
    userComments  = collectionRef.where('userID', '==', userID).get()

    path += "/" + userID + str(len(userComments))
    commentDocRef = db.document(path)

    commentDocRef.set({
        u'datePosted': firestore.SERVER_TIMESTAMP,
        u'userID': userID,
        u'comment': comment,
        u'path': path,
    })

def get_sub_comments(collection, comment_layer):
    allComments = []

    for commentDoc in collection.order_by('datePosted').stream():
        commentDict = commentDoc.to_dict()
        del commentDict["datePosted"]
        subCollection = collection.document(commentDoc.id).collection("c")

        commentDict["subComments"] = get_sub_comments(subCollection, comment_layer + 1)
        allComments.append(commentDict)

    return allComments

def get_post_comments(postID):
    postDoc    = db.collection('Comments').document(str(postID))
    collection = postDoc.collection("c")

    print(get_sub_comments(collection, 0))

users = ["John", "Laura", "Kishan", "Alex", "Andrew", "Tim", "Jake", "Tom", "Nick", "Collin"]

if __name__ == "__main__":
    post_comment(users[4], 1, "", "I liked this post")
    post_comment(users[5], 1, "", "I dont liked this post")
    post_comment(users[5], 1, "", "I liked this post")

    post_comment(users[0], 1, "", "I liked this post")
    post_comment(users[1], 1, "/c/John0", "I liked this post")
    post_comment(users[7], 1, "/c/John0/c/Laura0", "I liked this post")
    post_comment(users[8], 1, "/c/John0/c/Laura0", "I liked this post")

    get_post_comments(1)
    

