from django.shortcuts import render

# Create your views here.
from .models import *
import numpy as np

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
		self.relevance = post.embedding
		sumRelevances  = np.zeros(len(self.relevance))

		for hop in range(numHops):
			self.__get_scores_and_tails()
			self.scores = softmax(self.scores)
			self.__get_next_relevance()

			if len(self.tails) == 0:
				break
				
			for head in self.heads:
				self.prevHeads[head.get_id()] = True
			self.__find_new_heads() # also eliminates duplicates

			sumRelevances += self.relevance

		return sigmoid(np.dot(sumRelevances, post.embedding)) # TODO: add some regularizer that accounts for video's age

	def __get_scores_and_tails(self):
		self.scores, self.tails = list(), list()

		for headIndex, head in enumerate(self.heads):
			# [dict] keys: type of relationship, values: relationship matrix
			headRelations = head.get_all_relations() 

			for relationType in headRelations:
				if relationType not in self.relations:
					self.relations[relationType] = np.identity(self.lenEmbedding)

				score = np.dot( self.relevance, np.dot(self.relations[relationType], head.embedding) )
				self.scores.append(score)

				for NodeClass in [User, Post]:
					definition = dict(node_class=NodeClass, relation_type=relationType)

					for tail in match.Traversal(head, "traversal_name", definition).all():
						if tail.get_id() not in self.prevHeads:

							if relationType == "WATCHED" and isinstance(head, User):
								userRating = head.watched.relationship(tail).userRating
								self.tails.append((len(self.scores) - 1, userRating, tail))

							else:
								self.tails.append((len(self.scores) - 1, 1, tail))

	def __get_next_relevance(self):
		self.relevance = np.zeros(len(self.tails[0][2].embedding))
		for scoreIndex, k, tail in self.tails:
			self.relevance += self.scores[scoreIndex] * k * np.array(tail.embedding)

		return self.relevance

	def __find_new_heads(self):
		newTails = list()
		tailIDs  = dict()

		for t, (_, _, tail) in enumerate(self.tails):
			if self.scores[t] > .05 and tail.get_id() not in tailIDs:
				newTails.append(tail)
				tailIDs[tail.get_id()] = True

		self.heads = newTails


class PostNode:
	def __init__(self, postID, score):
		self.postID = postID
		self.score  = score
		self.next   = None
		self.prev   = None

class LinkedList:
	def __init__(self, maxSize=128):
		self.head    = None
		self.tail    = None
		self.size    = 0
		self.maxSize = maxSize

	def add_node(self, newNode):
		if self.head is None:
			self.head = newNode

		elif self.tail is None:
			self.add_tail(newNode)

		elif newNode.score > self.head.score:
			self.add_new_head(newNode)

		else:
			self.insert_node_after_head(newNode)

		self.size += 1

		if self.size > self.maxSize:
			self.remove_last_node()

	def add_tail(self, newNode):
		if newNode.score < self.head.score:
			self.tail      = newNode
			self.head.next = newNode
			self.tail.prev = self.head

		else:
			self.tail      = self.head
			self.tail.prev = newNode
			self.head      = newNode
			self.head.next = self.tail

	def add_new_head(self, newNode):
		newNode.next   = self.head
		self.head.prev = newNode
		self.head      = newNode

	def insert_node_after_head(self, newNode):
		searchNode = self.head
		while searchNode is not None and searchNode.score >= newNode.score:
			searchNode = searchNode.next

		if searchNode:
			newNode.next         = searchNode
			newNode.prev         = searchNode.prev
			searchNode.prev.next = newNode
			searchNode.prev      = newNode

		else:
			newNode.prev   = self.tail
			self.tail.next = newNode
			self.tail      = newNode

	def remove_last_node(self):
		self.tail      = self.tail.prev
		self.tail.next = None
		self.size     -= 1

	def get_node_ids(self):
		listOfNodes = [0] * self.size
		searchNode  = self.head

		for i in range(self.size):
			if searchNode is None:
				break

			listOfNodes[i] = searchNode.postID
			searchNode     = searchNode.next

		return listOfNodes
