from neomodel import config, StructuredNode, StructuredRel, properties, cardinality, match
import neomodel as neo 

import random
from abc import ABC, abstractmethod

class Node(ABC):
	@abstractmethod
	def get_all_relations(self):
		pass

	@abstractmethod
	def get_id(self):
		pass

config.ENCRYPTED_CONNECTION = False
config.DATABASE_URL = 'bolt://neo4j:PulpFiction1@localhost:7687' # default


class Watched(StructuredRel):
	timeWatched = properties.DateTimeProperty(default_now=True)
	userRating  = properties.FloatProperty()


class User(StructuredNode):
	userID    = properties.StringProperty(unique_index=True, required=True)
	embedding = properties.ArrayProperty(required=True)

	friends   = neo.Relationship('User', 'FRIENDS_WITH')
	following = neo.RelationshipTo('User', "IS_FOLLOWING") 
	followers = neo.RelationshipFrom('User', "IS_FOLLOWING")

	posts   = neo.RelationshipTo('Post', 'POSTED')
	watched = neo.RelationshipTo('Post', 'WATCHED', model=Watched)

	def get_all_relations(self):
		return {
			"FRIENDS_WITH": self.friends.all(), 
			"IS_FOLLOWING": self.following.all(),
			"POSTED":       self.posts.all(),
			"WATCHED":      self.watched.all(),
		}		

	def get_id(self):
		return self.userID


class Post(StructuredNode):
	postID      = properties.IntegerProperty(required=True, unique_index=True)
	timeCreated = properties.DateTimeProperty(default_now=True)
	embedding   = properties.ArrayProperty(required=True)

	creator    = neo.RelationshipFrom('User', 'POSTED', cardinality=cardinality.One)
	watched_by = neo.RelationshipFrom('User', 'WATCHED')

	def get_all_relations(self):
		return {
			"POSTED":  self.creator.all(),
			"WATCHED": self.watched_by.all(),
		}

	def get_id(self):
		return self.postID


if __name__ == "__main__":
	#pass
	user = User.nodes.get(userID="John")
	post = Post.nodes.get(postID=51)
	print(user.watched.relationship(post).userRating)
	#print(user.get_id())

	# print(vars(user)["friends"].all())

	# watched = user.watched
	# for watch in watched:
	# 	print(watch)
#userIDs = ["John", "Laura", "Jake", "Tom", "Kyra", "Andrew", "Collin"]

# allUsers = User.nodes.all()
# allPosts = Post.nodes.all()

# for user in allUsers:
# 	start = random.randint(0, len(allPosts))
# 	end   = random.randint(start, len(allPosts))

# 	for post in allPosts[start:end]:
# 		if post.creator.single().userID != user.userID:
# 			user.watched.connect(post, {"userRating":random.random()})

	# print("\n-=-=-=-=-" + user.userID + "-=-=-=-=-")
	# print(user.posts.all())
	# for creator in user.following.end_node():
	# 	print(creator.userID)

# for userID in userIDs:
# 	embedding    = [.1] * 10
# 	newUser = User(userID=userID, embedding=embedding)
# 	newUser.save()

# for userID in userIDs:
# 	start = random.randint(0, len(userIDs))
# 	end   = random.randint(start, len(userIDs))

# 	for creatorID in userIDs[start:end]:
# 		user    = User.nodes.get(userID=userID)
# 		creator = User.nodes.get(userID=creatorID)

# 		if userID != creatorID and user.friends.relationship(creator) is None:
# 			newFriends = user.following.connect(creator)

# allPosts = Post.nodes.all()
# for post in allPosts:
# 	#post.delete()
# 	# print(post.creator.single().userID)

# for userID in userIDs:
# 	user    = User.nodes.get(userID=userID)
# 	embedding = [.1] * 10

# 	for i in range(random.randint(0, 3)):
# 		newPost = Post(embedding=embedding)
# 		newPost.save()
# 		user.posts.connect(newPost)