class PostNode:
	def __init__(self, post, score):
		self.post  = post
		self.score = score
		self.next  = None
		self.prev  = None

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
			self.__add_tail(newNode)

		elif newNode.score > self.head.score:
			self.__add_new_head(newNode)

		else:
			self.__insert_node_after_head(newNode)

		self.size += 1

		if self.size > self.maxSize:
			self.__remove_last_node()

	def get_list_of_nodes(self):
		listOfNodes = list()
		searchNode  = self.head

		for i in range(self.size):
			if searchNode is None:
				break

			listOfNodes.append(searchNode.post.to_dict())  
			searchNode = searchNode.next

		return listOfNodes

	def __add_tail(self, newNode):
		if newNode.score < self.head.score:
			self.tail      = newNode
			self.head.next = newNode
			self.tail.prev = self.head

		else:
			self.tail      = self.head
			self.tail.prev = newNode
			self.head      = newNode
			self.head.next = self.tail

	def __add_new_head(self, newNode):
		newNode.next   = self.head
		self.head.prev = newNode
		self.head      = newNode

	def __insert_node_after_head(self, newNode):
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

	def __remove_last_node(self):
		self.tail      = self.tail.prev
		self.tail.next = None
		self.size     -= 1