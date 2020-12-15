import sys
import random

from models import *

def create_user(userID, embedding):
	return User(userID=userID, embedding=embedding).save()

def create_post(userID, postID, embedding):
	user    = User.nodes.get(userID=userID)
	newPost = Post(embedding=embedding, postID=postID).save()
	user.posts.connect(newPost)
	return newPost

def add_friend(friendID_0, friendID_1):
	friend_1 = User.nodes.get(userID=friendID_0)
	friend_2 = User.nodes.get(userID=friendID_1)

	try:
		friend_1.friends.connect(friend_2)
		return "Successfully made new friendship!"

	except:
		return str(sys.exc_info()[0])

def start_following(followerID, creatorID):
	follower = User.nodes.get(userID=followerID)
	creator  = User.nodes.get(userID=creatorID)

	try:
		follower.following.connect(creator)

	except:
		return str(sys.exc_info()[0])

def record_watched(userID, postID):
	user = User.nodes.get(userID=userID)
	post = Post.nodes.get(postID=postID)

	user.watched.connect(post, {"userRating":random.random()})

def delete_all():
	users = User.nodes.all()
	for user in users:
		user.delete()

	posts = Post.nodes.all()
	for post in posts:
		post.delete()

if __name__ == "__main__":
	delete_all()
	#userIDs = ["John", "Laura", "Jake", "Tom", "Kyra", "Andrew", "Collin", "Rob", "Jon", "Cersei", "Jorah", "Sam", "Emily", "Catylen", "Emma", "Kate", "Grace", "Danny", "James"]
	userIDs = ["John", "Laura", "Jake", "Tom", "Kyra", "Andrew", "Collin"]
	
	for j, userID in enumerate(userIDs):
		user = create_user(userID, [random.randint(0, 1) for i in range(10)])
		for i in range(random.randint(0, 2)):
			create_post(user.userID, j * 10 + i, [random.randint(0, 1) for i in range(10)])

	for userID in userIDs:
		start = random.randint(0, len(userIDs))
		end   = random.randint(start, len(userIDs)) // 3

		for friendID in userIDs[start:end]:
			if userID != friendID:
				add_friend(userID, friendID)

	for userID in userIDs:
		start = random.randint(0, len(userIDs))
		end   = random.randint(start, len(userIDs)) // 3

		for creatorID in userIDs[start:end]:
			if userID != creatorID:
				start_following(userID, creatorID)

	posts = Post.nodes.all()
	for userID in userIDs:
		start = random.randint(0, len(posts))
		end   = random.randint(start, len(posts)) // 3

		for post in posts[start:start + end]:
			if post.creator.single().userID != userID:
				record_watched(userID, post.postID)



