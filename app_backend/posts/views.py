import sys
import json
from datetime import datetime

from django.http import HttpResponse, JsonResponse
from django.apps import apps

from google.cloud import storage, firestore

User        = apps.get_model("models", "User")
Preferences = apps.get_model("models", "Preferences")
Profile     = apps.get_model("models", "Profile")
Post        = apps.get_model("models", "Post")

client = storage.Client(project="an-app-has-no-name")
bucket = client.get_bucket("an-app-has-no-name.appspot.com")

def watched_list(request, postID=None):
	try:
		# Creates a watchedBy entity to record that a user has watched a post. TODO: save the 
		# feedback for the post from the user (whether or not the user liked the post).
		if request.method == "POST":
			watchedJson = json.loads(request.body)
			user = User.objects.get(uid=watchedJson['uid'])
			post = Post.objects.get(postID=postID)

			# update_demographics(user, post, float(watchedJson["userRating"]))

			post.watchedBy.add(user)

			return HttpResponse(status=201)

	except:
		print(" [ERROR]", sys.exc_info())
		return HttpResponse(status=500)
		
def posts(request, uid=None):
	try:
		user = User.objects.get(uid=uid)

		# Returns a list of all of a user's posts. TODO: only return private post if user is friends
		# with the creator. 
		if request.method == "GET":
			userPostsList = []
			for post in user.created.all():
				userPostsList.append({
					"userID":   user.userID, 
					"uid":      user.uid,
					"username": user.username, 
					"postID":   post.postID, 
					"isImage":  post.isImage,
				})	
					
			return JsonResponse({"userPosts": userPostsList})

		# Receives meta-data about a post and the post's image of video file. Creates a new post
		# entity and uploads the post file to google storage in the right location and with the
		# right file extension and content type. 
		if request.method == "POST":
			newPostJson = json.loads(request.POST['json'])
			postID      = str(datetime.now().date()) + str(datetime.now().time())
			downloadURL = 'https://storage.googleapis.com/an-app-has-no-name.appspot.com/'

			if newPostJson['isImage']:
				postFile          = "%s/%s.png" % (uid, postID)		
				blob              = bucket.blob(postFile)
				blob.content_type = "image/png"
			else:
				postFile          = "%s/%s.mp4" % (uid, postID)		
				blob              = bucket.blob(postFile)
				blob.content_type = "video/mp4"

			downloadURL += postFile
			blob.upload_from_file(request.FILES['media'])
			blob.make_public()

			Post.objects.create(
				postID      = postID,
				preferences = Preferences.objects.create(),
				creator     = user,
				isImage	    = newPostJson["isImage"],
				isPrivate   = newPostJson["isPrivate"],
				downloadURL = downloadURL
			)

			return HttpResponse(status=201)

	except:
		print(" [ERROR]", sys.exc_info())
		return HttpResponse(status=500)

def post(request, uid=None, postID=None):
	try:
		post = Post.objects.get(postID=postID)
		if post.creator.uid != uid:
			return HttpResponse(status=401)

		if request.method == "POST":
			post.isPrivate = json.loads(request.body)["isPrivate"]
			post.save()

			return HttpResponse(status=200)

		if request.method == "DELETE":
			post.delete_post()
			
			return HttpResponse(status=200)

	except:
		print(" [ERROR]", sys.exc_info())
		return HttpResponse(status=500)