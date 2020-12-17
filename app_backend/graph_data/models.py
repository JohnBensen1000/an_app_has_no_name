from django.db import models

# Create your models here.
from neomodel import config, StructuredNode, StructuredRel, properties, cardinality, match, Relationship, RelationshipTo, RelationshipFrom


config.ENCRYPTED_CONNECTION = False
config.DATABASE_URL = 'bolt://neo4j:PulpFiction1@localhost:7687' # default


class Watched(StructuredRel):
	timeWatched = properties.DateTimeProperty(default_now=True)
	userRating  = properties.FloatProperty()


class UserNode(StructuredNode):
	userID    = properties.StringProperty(unique_index=True, required=True)
	embedding = properties.ArrayProperty(required=True)

	friends   = Relationship('UserNode', 'FRIENDS_WITH')
	following = RelationshipTo('UserNode', "IS_FOLLOWING") 
	followers = RelationshipFrom('UserNode', "IS_FOLLOWING")

	posts   = RelationshipTo('PostNode', 'POSTED')
	watched = RelationshipTo('PostNode', 'WATCHED', model=Watched)

	def get_all_relations(self):
		return {
			"FRIENDS_WITH": self.friends.all(), 
			"IS_FOLLOWING": self.following.all(),
			"POSTED":       self.posts.all(),
			"WATCHED":      self.watched.all(),
		}		

	def get_id(self):
		return self.userID


class PostNode(StructuredNode):
	postID      = properties.IntegerProperty(required=True, unique_index=True)
	timeCreated = properties.DateTimeProperty(default_now=True)
	embedding   = properties.ArrayProperty(required=True)

	creator    = RelationshipFrom('UserNode', 'POSTED', cardinality=cardinality.One)
	watched_by = RelationshipFrom('UserNode', 'WATCHED')

	def get_all_relations(self):
		return {
			"POSTED":  self.creator.all(),
			"WATCHED": self.watched_by.all(),
		}

	def get_id(self):
		return self.postID


if __name__ == "__main__":
	pass
	#UserNode(userID="Jake", embedding=[0.8582748391403945, 0.46282480586028407, 0.9090647732570551, 0.8198452978521688, 0.7558556331497358, 0.2543528836965928, 0.28900423558527155, 0.2185256623470263, 0.3240233675409879, 0.025704486063794274, 0.5478645463346681, 0.8970670055337764, 0.8680123098770661, 0.41933702971639875, 0.3178740785192653, 0.4568525749810908, 0.5974022829691965]).save()
	# users = UserNode.nodes.all()
	# for user in users:
	# 	user.delete()

	# posts = PostNode.nodes.all()
	# for post in posts:
	# 	post.delete()