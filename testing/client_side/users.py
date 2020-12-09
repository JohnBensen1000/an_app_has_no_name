import requests
import json
import random

users = ["John", "Laura", "Kishan", "Alex", "Andrew", "Tim", "Jake", "Tom", "Nick", "Collin"]


def create_account(url):
	url += "client_side/users/create_new_user/"

	for username in users:
		userID            = username + "1000"
		preferredLanguage = "English"
		username          = username
		demographics      = [random.uniform(0, 1) for a in range(17)]

		email             = username + "@gmail.com"
		phone             = "15164979872"

		clientRequest = {
			"userID":           userID,          
			"preferredLanguage":preferredLanguage,
			"username":         username,          
			"demographics":     str(demographics),  
			"email":            email,             
			"phone":            phone,          
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


def start_following(url):
	url += "client_side/users/start_following/"

	follower = users[0] + "1000"

	for creator in users[2:5]:
		clientRequest = {
			"follower":follower,
			"creator": creator + "1000"
		}

		response=requests.post(url, clientRequest)
		print(response.text)

	creator = users[7] + "1000"

	for follower in users[3:7]:
		clientRequest = {
			"follower":follower + "1000",
			"creator": creator
		}

		response=requests.post(url, clientRequest)
		print(response.text)


def get_following(url):
	url += "client_side/users/get_followings/"

	for follower in users:
		clientRequest = {
			"follower":follower + "1000"
		}

		response = requests.get(url, clientRequest)
		print(response.text)


def get_followers(url):
	url += "client_side/users/get_followers/"

	for creator in users:
		clientRequest = {
			"creator":creator + "1000"
		}

		response = requests.get(url, clientRequest)
		print(response.text)


def become_friends(url):
	url += "client_side/users/become_friends/"

	friend_1 = users[1] + "1000"
	for friend_2 in users[2: ]:
		clientRequest = {
			"friend_1": friend_1,
			"friend_2": friend_2 + "1000",
		}
		response = requests.post(url, clientRequest)
		print(response.text)

	friend_1 = users[3] + "1000"
	for friend_2 in users[ :3]:
		clientRequest = {
			"friend_1": friend_1,
			"friend_2": friend_2 + "1000",
		}
		response = requests.post(url, clientRequest)
		print(response.text)


def get_friends(url):
	url += "client_side/users/get_friends/"

	for user in users:
		print(user)
		clientRequest = {
			"user": user + "1000"
		}
		response = requests.get(url, clientRequest)
		print(response.text, "\n")
