import requests
import json

def create_account(url):
	url += "client_side/users/create_new_user/"

	demographics      = [.75 if a % 4 == 1 else .2 for a in range(17)]
	userID            = input("What is your user ID? ")
	preferredLanguage = "English"
	username          = input("What is your desired username? ")

	clientRequest = {
		"demographics":str(demographics),
		"userID":userID,
		"preferredLanguage":preferredLanguage,
		"username":username
	}

	response = requests.post(url, clientRequest)
	print(response.text)

def find_creators(url):
	url += "client_side/users/search_creators/"

	print("Search for users, type CTRL-C to exit.")
	try:
		while True:
			searchString  = input()
			clientRequest = {
				"searchString":searchString
			} 

			response = requests.get(url, clientRequest)
			print(response.text)

	except KeyboardInterrupt:
		pass
