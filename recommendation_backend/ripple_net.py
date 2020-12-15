from models import *

import numpy as np
import scipy as sp 
import logging
import time

# class Logger:
# 	def __init__(self, fileName="recommend_log.log"):
# 		logging.basicConfig(filename=fileName, 
# 		                    format='%(asctime)s %(message)s', 
# 		                    filemode='w') 
		  
# 		self.logger = logging.getLogger() 	  
# 		self.logger.setLevel(logging.DEBUG) 

# 	def log_start_seach(self, user, post):
# 		self.logger.debug(" [DEBUG] Starting relevance search for user: " + user.get_id() + " and " + str(post.get_id()))

# 	def log_new_hop(self, hop):
# 		self.logger.debug(" [DEBUG] -=-=-= New Hop: %d =-=-=-" % hop)

# 	def log_tail_scores(self, relevance, heads, relationships, tails, scores):
# 		self.logger.debug(" [DEBUG] Relevance: " + str([round(r, 3) for r in relevance]))

# 		for i, (headID, relationship) in enumerate(relationships):
# 			self.logger.debug(" [DEBUG] %8s: %s -score: %s-> %8s: %s" % 
# 				(heads[headID].get_id(), str([round(r, 3) for r in heads[headID].embedding]), 
# 				 round(scores[i], 3),
# 				 tails[i].get_id(),      str([round(r, 3) for r in tails[i].embedding])))

# 	def log_relevance(self, relevance):
# 		self.logger.debug(" [DEBUG] New relevance vector: " + str([round(r, 3) for r in relevance]))

# 	def log_heads(self, heads):
# 		self.logger.debug(" [DEBUG] New heads: " + str([head.get_id() for head in heads]))


def softmax(x):
	return (np.exp(x)) / np.sum(np.exp(x))

def sigmoid(x):
	return x / (1 + abs(x))

class RippleNet:
	# algorithm found in paper https://arxiv.org/pdf/1803.03467.pdf

	def __init__(self, lenEmbedding, logger=None, loadRelations=None):
		self.relations    = {}
		self.lenEmbedding = lenEmbedding
		self.logger       = logger

	def find_relevance(self, user, post, numHops):
		self.prevHeads = {user.get_id(): True}
		self.heads     = user.watched.all()
		relevance = post.embedding
		relAll    = np.zeros(len(relevance))

		for hop in range(numHops):
			self.__get_relationships_and_tails()
			self.__get_scores(relevance)
			if len(self.tails) == 0:
				break
				
			relevance = self.__get_next_relevance()
			self.__find_new_heads() # also eliminates duplicates
			
			for head in self.heads:
				self.prevHeads[head.get_id()] = True

			relAll += relevance

		return sigmoid(np.dot(relAll, post.embedding)) # add some regularizer that accounts for video's age

	def __get_relationships_and_tails(self):
		startTime = time.time()
		relationships, tails = list(), list()

		for headIndex, head in enumerate(self.heads):
			startTime = time.time()
			headRelations = head.get_all_relations()

			for relationType in headRelations:
				if relationType not in self.relations:
					self.relations[relationType] = np.identity(self.lenEmbedding)

				for NodeClass in [User, Post]:
					definition = dict(node_class=NodeClass, relation_type=relationType)
					headTails  = match.Traversal(head, "traversal_name", definition).all()

					for tail in headTails:
						if tail.get_id() not in self.prevHeads:
							tails.append(tail)

							if relationType == "WATCHED" and isinstance(head, User):
								userRating = head.watched.relationship(tail).userRating
								relationships.append((headIndex, self.relations[relationType] * userRating))

							else:
								relationships.append((headIndex, self.relations[relationType]))

		self.relationships, self.tails = relationships, tails

	def __get_scores(self, relevance):
		scores = [0] * len(self.relationships)
		for i, (headIndex, relationship) in enumerate(self.relationships):
			scores[i] = np.dot( relevance, np.dot(relationship, self.heads[headIndex].embedding) )

		self.scores = softmax(scores) 

	def __get_next_relevance(self):
		relevance = np.zeros(len(self.tails[0].embedding))
		for s, score in enumerate(self.scores):
			relevance += score * np.array(self.tails[s].embedding)

		return relevance

	def __find_new_heads(self):
		newTails = list()
		tailIDs  = dict()

		for t, tail in enumerate(self.tails):
			if self.scores[t] > .05 and tail.get_id() not in tailIDs:
				newTails.append(tail)
				tailIDs[tail.get_id()] = True

		self.heads = newTails

if __name__ == "__main__":
	startTime = time.time()
	for i in range(10):
		rippleNet = RippleNet(10)
		user = User.nodes.all()[0]
		post = Post.nodes.all()[0]
		rippleNet.find_relevance(user, post, 3)
		#print(rippleNet.find_relevance(user, post, 3))

	print(time.time() - startTime)

	logging.shutdown()