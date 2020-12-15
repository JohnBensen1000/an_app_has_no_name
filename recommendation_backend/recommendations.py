from models import *

import numpy as np
import scipy as sp 
import logging

class Logger:
	def __init__(self, fileName="recommend_log.log"):
		logging.basicConfig(filename=fileName, 
		                    format='%(asctime)s %(message)s', 
		                    filemode='w') 
		  
		self.logger = logging.getLogger() 	  
		self.logger.setLevel(logging.DEBUG) 

	def log_start_seach(self, user, post):
		self.logger.debug(" [DEBUG] Starting relevance search for user: " + user.get_id() + " and " + str(post.get_id()))

	def log_new_hop(self, hop):
		self.logger.debug(" [DEBUG] -=-=-= New Hop: %d =-=-=-" % hop)

	def log_tail_scores(self, relevance, heads, relationships, tails, scores):
		self.logger.debug(" [DEBUG] Relevance: " + str([round(r, 3) for r in relevance]))

		for i, (headID, relationship) in enumerate(relationships):
			self.logger.debug(" [DEBUG] %8s: %s -score: %s-> %8s: %s" % 
				(heads[headID].get_id(), str([round(r, 3) for r in heads[headID].embedding]), 
				 round(scores[i], 3),
				 tails[i].get_id(),      str([round(r, 3) for r in tails[i].embedding])))

	def log_relevance(self, relevance):
		self.logger.debug(" [DEBUG] New relevance vector: " + str([round(r, 3) for r in relevance]))

	def log_heads(self, heads):
		self.logger.debug(" [DEBUG] New heads: " + str([head.get_id() for head in heads]))


def softmax(x):
	return (np.exp(x)) / np.sum(np.exp(x))

def sigmoid(x):
	return 1 / (1 + abs(x))

class RippleNet:
	# algorithm found in paper https://arxiv.org/pdf/1803.03467.pdf

	def __init__(self, lenEmbedding, logger, loadRelations=None):
		self.relations    = {}
		self.lenEmbedding = lenEmbedding
		self.logger       = logger

	def find_relevance(self, user, post, numHops):
		self.logger.log_start_seach(user, post)

		relevance = post.embedding
		relAll    = np.zeros(len(relevance))
		heads     = user.watched.all()

		prevHeads = [user]

		for hop in range(numHops):
			self.logger.log_new_hop(hop)

			relationships, tails = self.get_relationships_and_tails(heads, prevHeads)
			scores               = self.get_scores(relevance, relationships, heads)
			self.logger.log_tail_scores(relevance, heads, relationships, tails, scores)

			if len(tails) == 0:
				break
				
			relevance = self.get_next_relevance(scores, tails)
			heads     = self.eliminate_duplicates(tails)
			self.logger.log_relevance(relevance)
			self.logger.log_heads(heads)
			
			prevHeads += heads
			relAll    += relevance

		userPostMatch = sigmoid(np.dot(relAll, post.embedding)) # add some regularizer that accounts for video's age
		#logger.log_user_post_match(userPostMatch)
		return userPostMatch

	def get_relationships_and_tails(self, heads, prevHeads):
		relationships, tails = list(), list()

		for headID, head in enumerate(heads):
			headRelations = head.get_all_relations()

			for relationType in headRelations.keys():
				if relationType not in self.relations.keys():
					self.relations[relationType] = np.identity(self.lenEmbedding)

				for NodeClass in [User, Post]:
					definition = dict(node_class=NodeClass, relation_type=relationType)
					headTails  = match.Traversal(head, "traversal_name", definition).all()

					for tail in headTails:
						if tail not in prevHeads:
							tails.append(tail)

							if relationType == "WATCHED" and isinstance(head, User):
								userRating = head.watched.relationship(tail).userRating
								relationships.append((headID, self.relations[relationType] * userRating))

							else:
								relationships.append((headID, self.relations[relationType]))

		return relationships, tails

	def get_scores(self, relevance, relationships, heads):
		scores = list()
		for headID, relationship in relationships:
			score = np.dot( relevance, np.dot(relationship, heads[headID].embedding) )
			scores.append(score) 

		return softmax(scores) 

	def get_next_relevance(self, scores, tails):
		relevance = np.zeros(len(tails[0].embedding))
		for s, score in enumerate(scores):
			relevance += score * np.array(tails[s].embedding)

		return relevance

	def eliminate_duplicates(self, tails):
		newTails = list()
		for tail in tails:
			if tail not in newTails:
				newTails.append(tail)

		return newTails


if __name__ == "__main__":
	rippleNet = RippleNet(10, Logger())
	user = User.nodes.all()[0]
	post = Post.nodes.all()[0]

	print(rippleNet.find_relevance(user, post, 3))



