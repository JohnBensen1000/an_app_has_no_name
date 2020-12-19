import random
import requests

url = "http://127.0.0.1:8000/"

print("What do you want to do?")
print("		[0] Search for creators.")
print("		[1] Create new user account.")
print("		[2] Get user account information.")
print("		[3] Delete all accounts.")
print("		[4] Get followings.")
print("		[5] Start following.")
print("		[6] Delete followings.")
print("		[7] Get friends.")
print("		[8] Start being friends.")
print("		[9] Stop being friends.")

option = int(input("Option: "))

users = ["John", "Laura", "Kishan", "Alex", "Andrew", "Tim", "Jake", "Tom", "Nick", "Collin"]

if option == 0:
	pass

if option == 1:
	url += "users/new_user/"

	for username in users:
		userID            = username + "1000"
		preferredLanguage = "English"
		username          = username
		demographics      = [random.uniform(0, 1) for a in range(19)]

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

if option == 2:
	for user in users:
		userID = user + "1000"
		newUrl = url + "users/%s/" % userID

		response = requests.get(newUrl)
		print(response.text)

if option == 3:
	for user in users:
		userID = user + "1000"
		newUrl = url + "users/%s/" % userID

		response = requests.delete(newUrl)
		print(response.text)		

if option == 4:
	for user in users:
		print("\n-=-=-=-=-=-=-=-=-=-=-=-=-")
		print("User: " + user)
		newUrl = url + "users/%s/following/" % (user + "1000")

		response = requests.get(newUrl)
		print(response.text)

if option == 5:
	for user in users:
		follower = user + "1000"
		start = random.randint(0, len(users))
		end   = random.randint(start, len(users)) // 2

		for creator in users[start:end]:
			if creator != user:
				newUrl = url + "users/%s/following/new/" % follower

				clientRequest = {
					"creatorID": creator + "1000"
				}
				response = requests.post(newUrl, clientRequest)
				print(response.text)	

if option == 6:
	for user in users:
		for creator in users:
			if creator != user:
				userID, creatorID = user + "1000", creator + "1000"
				newUrl = url + "users/%s/following/%s/" % (userID, creatorID)

				response = requests.delete(newUrl)
				print(response.text)

if option == 7:
	for user in users:
		print("\n-=-=-=-=-=-=-=-=-=-=-=-=-")
		print("User: " + user)
		newUrl = url + "users/%s/friends/" % (user + "1000")

		response = requests.get(newUrl)
		print(response.text)

if option == 8:
	for user in users:
		userID = user + "1000"
		start = random.randint(0, len(users))
		end   = random.randint(start, len(users)) // 2

		for newFriend in users[start:end]:
			if newFriend != user:
				newUrl = url + "users/%s/friends/new/" % userID

				clientRequest = {
					"newFriendID": newFriend + "1000"
				}
				response = requests.post(newUrl, clientRequest)
				print(response.text)	

if option == 9:
	for user in users:
		for friend in users:
			if friend != user:
				userID, friendID = user + "1000", friend + "1000"
				newUrl = url + "users/%s/friends/%s/" % (userID, friendID)

				response = requests.delete(newUrl)
				print(response.text)	