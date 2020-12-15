from models import *
from ripple_net import RippleNet

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
			newNode.next   = self.head
			self.head.prev = newNode
			self.head      = newNode

		else:
			self.insert_node_after_head(newNode)

		self.size += 1

		if self.size > self.maxSize:
			self.tail      = self.tail.prev
			self.tail.next = None
			self.size     -= 1

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

	def get_node_ids(self):
		listOfNodes = [0] * self.size
		searchNode  = self.head

		for i in range(self.size):
			if searchNode is None:
				break

			listOfNodes[i] = searchNode.postID
			searchNode     = searchNode.next

		return listOfNodes


def run_recommendations(userID):
	user       = User.nodes.get(userID=userID)
	linkedList = LinkedList()
	rippleNet  = RippleNet(10)

	userWatched = user.watched.all()
	userPosted  = user.posts.all()

	for post in Post.nodes.all():
		if post not in userPosted and post not in userWatched:
			newNode = PostNode(post.get_id(), rippleNet.find_relevance(user, post, 1))
			linkedList.add_node(newNode)

	return linkedList.get_node_ids()


if __name__ == "__main__":
	print(run_recommendations('Tom'))
	# linkedList = LinkedList()
	# scores = [random.random() for i in range(10)]
	# print(scores)
	# ids    = range(10)

	# for i in range(10):
	# 	if i not in [2, 4, 5]:
	# 		newNode = PostNode(ids[i], scores[i])
	# 		linkedList.add_node(newNode)

	# 		print(linkedList.get_node_ids())






