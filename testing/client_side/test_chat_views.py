import random
import requests
import socket

url = "http://127.0.0.1:8000/"

def start_listening(userID):
	host = '127.0.0.1'
	port = 5812
  
	s = socket.socket(socket.AF_INET,socket.SOCK_STREAM) 
	s.connect((host,port)) 

	try:
		s.send(userID.encode('ascii')) 
		while True: 
			data = s.recv(1024) 

			print('Received from the server :',str(data.decode('ascii'))) 

	except KeyboardInterrupt:
		s.close()


def get_all_chats(userID):
	url = "http://127.0.0.1:8000/chats/%s/" % userID
	response = requests.get(url)
	print(response.text)


def start_direct_chat(userID, recieverID):
	url = "http://127.0.0.1:8000/chats/%s/new_direct/" % userID
	requestJson = {
		"recieverID": recieverID,
	}
	response = requests.post(url, requestJson)
	print(response.text)

def send_direct_chat(userID, recieverID):
	chatID = userID + recieverID if userID < recieverID else recieverID + userID
	url = "http://127.0.0.1:8000/chats/%s/%s/" % (userID, chatID)

	message = input("Message: ")
	requestJson = {
		"message": message,
	}
	response = requests.post(url, requestJson)
	print(response.text)


def start_group_chat(userID, groupchatID):
	url = "http://127.0.0.1:8000/chats/%s/new_group/" % (userID)
	requestJson = {
		"groupchatID": groupchatID,
	}
	response = requests.post(url, requestJson)
	print(response.text)

def send_group_chat(userID, groupchatID):
	url = "http://127.0.0.1:8000/chats/%s/%s/" % (userID, groupchatID)

	message = input("Message: ")
	requestJson = {
		"message": message,
	}
	response = requests.post(url, requestJson)
	print(response.text)

def add_user_to_group_chat(userID, groupchatID):
	newMember = input("UserID of new member: ")

	url = "http://127.0.0.1:8000/chats/%s/%s/%s/" % (userID, groupchatID, newMember)
	response = requests.post(url)
	print(response.text)


def start_sending(userID):
	while True:
		print("What do you want to do?")
		print("		[0] Get all chats")
		print("		[1] Start Direct Chat")
		print("		[2] Send Direct Chat ")
		print("		[3] Start Group Chat")
		print("		[4] Send Group Chat")
		print("		[5] Add user to groupchat")
		print("		[6] Remove user from groupchat")

		option = int(input("Option: "))
		
		if option == 0:
			get_all_chats(userID)

		if option == 1:
			recieverID = input("Who do you want to have a chat with? ")
			start_direct_chat(userID, recieverID)

		if option == 2:
			recieverID = input("Who do you want to have a chat with? ")
			send_direct_chat(userID, recieverID)

		if option == 3:
			groupchatID = input("What do you want to name your group chat? ")
			start_group_chat(userID, groupchatID)

		if option == 4:
			groupchatID = input("What is group chat? ")
			send_group_chat(userID, groupchatID)

		if option == 5:
			groupchatID = input("What is group chat? ")
			add_user_to_group_chat(userID, groupchatID)


if __name__ == "__main__":
	userID = input("User ID: ")

	print("Do you want to start listening [0] or start sending [1]?")
	option = int(input("Option: "))

	if option == 0:
		start_listening(userID)
	elif option == 1:
		start_sending(userID)