import queue
import threading
import socket 

class ChatsManager:
	def __init__(self):
		self.queueDict = {}

		host, port = "", 5809

		self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
		self.s.bind((host, port)) 
		self.s.listen(5) 

	def start(self):
		self.mainThread = threading.Thread(target=self.__listen_for_connections)
		self.mainThread.start()

	def send_message(self, userID, message):
		if userID in self.queueDict:
			self.queueDict[userID].put(message.encode('ascii'))

	def __listen_for_connections(self):
		while True:
			client, addr = self.s.accept() 
			userID       = client.recv(1024).decode('ascii')
			userQueue    = queue.Queue()
			self.queueDict[userID] = userQueue

			threading.Thread(target=self.__manage_messages, 
				args=(client, userID, userQueue)).start()  

	def __manage_messages(self, client, userID, userQueue):
		try:
			while True:
				client.send(userQueue.get()) 

		except BrokenPipeError:
			del self.queueDict[userID]
			client.close()