import concurrent.futures
import logging
import queue
import random
import threading
import time
import socket 

class Messages:
	def __init__(self):
		self.queueDict = {}

		host, port = "", 5809

		self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
		self.s.bind((host, port)) 
		self.s.listen(5) 

	def start(self):
		self.mainThread = threading.Thread(target=self.__listen_for_connections)
		self.mainThread.start()

	def send(self, userID, message):
		if userID in self.queueDict:
			self.queueDict[userID].put(message.encode('ascii'))

	def __listen_for_connections(self):
		while True:
			client, addr = self.s.accept() 
			userID       = client.recv(1024).decode('ascii')
			userQueue    = queue.Queue()
			self.queueDict[userID] = userQueue

			threading.Thread(target=self.__send_messages, 
				args=(client, userID, userQueue)).start()  

	def __send_messages(self, client, userID, userQueue):
		try:
			while True:
				client.send(userQueue.get()) 

		except BrokenPipeError:
			del self.queueDict[userID]
			client.close()


if __name__ == "__main__":
	messages = Messages()
	messages.start()
	print("Started messaging")
	while True:
		time.sleep(1)
		messages.send("john", "Hello")
		messages.send("laura", "Hi")

	