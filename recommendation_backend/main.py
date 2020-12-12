from neomodel import config, StructuredNode, StructuredRel, properties, cardinality
import neomodel as neo 
import random


config.ENCRYPTED_CONNECTION = False
config.DATABASE_URL = 'bolt://neo4j:PulpFiction1@localhost:7687' # default


class Watched(StructuredRel):
	timeWatched = properties.DateTimeProperty(default_now=True)
	userRating  = properties.FloatProperty()


class User(StructuredNode):
    userID = properties.StringProperty(unique_index=True, required=True)
    demo   = properties.ArrayProperty(required=True)

    friends   = neo.Relationship('User', 'FRIENDS_WITH')
    following = neo.RelationshipTo('User', "IS_FOLLOWING") 
    followers = neo.RelationshipFrom('User', "IS_FOLLOWING")

    posts   = neo.RelationshipTo('Post', 'POSTED')
    watched = neo.RelationshipTo('Post', 'WATCHED', model=Watched)


class Post(StructuredNode):
	postID      = properties.IntegerProperty(required=True, unique_index=True)
	timeCreated = properties.DateTimeProperty(default_now=True)
	demo        = properties.ArrayProperty(required=True)

	creator    = neo.RelationshipFrom('User', 'POSTED', cardinality=cardinality.One)
	watched_by = neo.RelationshipFrom('User', 'WATCHED')


userIDs = ["John", "Laura", "Jake", "Tom", "Kyra", "Andrew", "Collin"]

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
# 	demo    = [.1] * 10
# 	newUser = User(userID=userID, demo=demo)
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
# 	demo    = [.1] * 10

# 	for i in range(random.randint(0, 3)):
# 		newPost = Post(demo=demo)
# 		newPost.save()
# 		user.posts.connect(newPost)