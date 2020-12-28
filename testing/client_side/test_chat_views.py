import random
import requests
import socket

url = "http://127.0.0.1:8000/"

def start_listening(userID):
	host = '127.0.0.1'
	port = 5809
  
	s = socket.socket(socket.AF_INET,socket.SOCK_STREAM) 
	s.connect((host,port)) 

	try:
		s.send(userID.encode('ascii')) 
		while True: 
			data = s.recv(1024) 

			print('Received from the server :',str(data.decode('ascii'))) 

	except KeyboardInterrupt:
		s.close()

def start_sending(userID, recieverID):
	url = "http://127.0.0.1:8000/chats/%s/direct/%s/" % (userID, recieverID)

	while True:
		message = input("Message: ")
		requestJson = {
			"message": message,
		}
		response = requests.post(url, requestJson)
		print(response.text)

if __name__ == "__main__":
	userID = input("User ID: ")

	print("Do you want to start listening [0] or start sending [1]?")
	option = int(input("Option: "))

	if option == 0:
		start_listening(userID)
	elif option == 1:
		recieverID = input("Who do you want to have a chat with? ")
		start_sending(userID, recieverID)