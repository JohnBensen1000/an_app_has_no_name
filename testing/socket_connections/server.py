import concurrent.futures
import logging
import queue
import random
import threading
import time

def send_messages_to_user(client, queue, event):
	while not event.is_set():
		client.send(queue.get()) 

def listen_for_connections(s, queueDict, eventDict):
	while True
		client, addr = s.accept() 
		userID = client.recv(1024) 
		queue  = queue.Queue()
		event  = threading.Event()

		queueDict[userID], eventDict[userID] = queue, event

		print("Starting new thread for user: %s" % userID)
		newThread = threading.Thread(target=send_messages_to_user, args=(c, queue, event, ))  
		newThread.start()

class Messages:
	def __init__(self):
		self.queueDict = {}
		self.eventDict = {}

		host, port = "", 5804

		self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
		self.s.bind((host, port)) 
		self.s.listen(5) 

	def start(self):
		with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
			executor.submit(start_connections, self.s, self.queueDict, self.eventDict)

	def send(self, userID, message):
		if userID in self.queueDict:
			self.queueDict[userID].put(message)

	def stop_queue(self, userID):
		if userID in self.eventDict:
			self.eventDict[userID].set()
			del self.queueDict[userID]
			del self.eventDict[userID]

	def stop(self):
		for userID in self.queueDict:
			self.stop_queue(userID)




# def producer(queue, event):
#     """Pretend we're getting a number from the network."""
#     while not event.is_set():
#         message = random.randint(1, 101)
#         logging.info("Producer got message: %s", message)
#         queue.put(message)

#     logging.info("Producer received event. Exiting")

# def consumer(queue, event):
#     """Pretend we're saving a number in the database."""
#     while not event.is_set() or not queue.empty():
#         message = queue.get()
#         logging.info(
#             "Consumer storing message: %s (size=%d)", message, queue.qsize()
#         )

#     logging.info("Consumer received event. Exiting")

# if __name__ == "__main__":
#     format = "%(asctime)s: %(message)s"
#     logging.basicConfig(format=format, level=logging.INFO,
#                         datefmt="%H:%M:%S")

#     pipeline = queue.Queue(maxsize=10)
#     event = threading.Event()
#     with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
#         executor.submit(producer, pipeline, event)
#         executor.submit(consumer, pipeline, event)

#         time.sleep(0.001)
#         logging.info("Main: about to set event")
#         event.set()


# # import socket programming library 
# import socket 
# import threading 
# import json
# import queue

# def send_messages_to_user(client, messageQueue, userEvent):
# 	while not userEvent.is_set():
# 		client.send(messageQueue.get()) 

# def listen_for_new_connections(s):
# 	messageQueueDict = {}
# 	clientEventDict  = {}

# 	while True: 
# 		client, addr = s.accept() 
# 		print('Connected to :', addr[0], ':', addr[1]) 

# 		userID       = client.recv(1024) 
# 		messageQueue = queue.Queue()
# 		clientEvent  = threading.Event()

# 		messageQueueDict[userID] = messageQueue
# 		clientEventDict[userID]  = clientEvent

# 		print("Starting new thread for user: %s" % userID)
# 		newThread = threading.Thread(target=send_messages_to_user, args=(c, messageQueue, clientEvent, ))  
# 		newThread.start()

# 	s.close() 

# if __name__ == "__main__":
# 	host = "" 
# 	port = 5804

# 	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
# 	s.bind((host, port)) 
# 	print("socket binded to port", port) 

# 	s.listen(5) 
# 	print("socket is listening") 

# 	listen_for_new_connections(s)
  

# index = [0]

# def run_client_thread(c, index): 
# 	print("Started thread.")
# 	while True: 

# 		data = c.recv(1024) 
# 		print("Recieved message: %s. Index: " % (data), index)
# 		index.append(1)

# 		if not data: 
# 			print('Bye') 
# 			break

# 		data = data[::-1] 
# 		c.send(data) 

# 	c.close() 
  
# host = "" 
# port = 5804

# s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
# s.bind((host, port)) 
# print("socket binded to port", port) 

# s.listen(5) 
# print("socket is listening") 

# while True: 
# 	print("x")
# 	c, addr = s.accept() 

# 	print('Connected to :', addr[0], ':', addr[1]) 
# 	newThread = threading.Thread(target=run_client_thread, args=(c, index, ))  
# 	newThread.start()

# s.close() 
  

