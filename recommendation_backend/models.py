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
	pass