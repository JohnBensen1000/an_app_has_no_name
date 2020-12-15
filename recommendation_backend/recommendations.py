from models import *

import numpy as np
import scipy as sp 
import logging

logging.basicConfig(filename="recommend_log.log", 
                    format='%(message)s', 
                    filemode='w')
logger = logging.getLogger()

def softmax(x):
	return (np.exp(x)) / np.sum(np.exp(x))


class RippleNet:
	# algorithm found in paper https://arxiv.org/pdf/1803.03467.pdf

	def __init__(self, lenEmbedding, loadRelations=None):
		self.relations    = {}
		self.lenEmbedding = lenEmbedding

	def find_relevance(self, user, post, numHops):
		self.user, self.post = user, post

		o      = np.array(post.embedding)
		oList  = np.zeros(self.lenEmbedding)
		heads  = [watched for watched in user.watched]
		print("Starting relevance search with heads:" + str([head.postID for head in heads]))

		for hop in range(numHops):
			heads, o = self.get_next_hop(heads, o)
			oList += o

		return np.dot(np.array(post.embedding).T, oList)

	def get_next_hop(self, heads, o):
		tails, scores = list(), list()

		for head in heads:
			# creates a dict with keys = Node attributes' names and values = Node attributes' values
			headRelations = head.get_all_relations()

			for relationType in headRelations.keys():
				if relationType not in self.relations.keys():
					self.relations[relationType] = np.identity(self.lenEmbedding)

				for NodeClass in [User, Post]:
					definition = dict(node_class=NodeClass, relation_type=relationType)
					headTails  = match.Traversal(head, "traversal_name", definition).all()

					if self.user in headTails:
						headTails.remove(self.user)

					if len(headTails) > 0:	
						scores += [np.dot(o, np.dot(self.relations[relationType], head.embedding))] * len(headTails)
						tails  += headTails

		o     *= 0
		scores = softmax(scores)

		for t, tail in enumerate(tails):
			o += scores[t] * np.array(tail.embedding)

		return tails, o

if __name__ == "__main__":
	rippleNet = RippleNet(10)
	user = User.nodes.all()[0]
	post = Post.nodes.all()[0]

	print(rippleNet.find_relevance(user, post, 2))



