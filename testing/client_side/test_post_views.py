import random
import requests
import json

url = "http://127.0.0.1:8000/"

print("What do you want to do?")
print("		[0] Get created posts.")
print("		[1] Create new post.")
print("		[2] Record watched video.")

option = int(input("Option: "))

users = ["John", "Laura", "Kishan", "Alex", "Andrew", "Tim", "Jake", "Tom", "Nick", "Collin"]

if option == 0:
	for user in users:
		print("\n-=-=-=-=-=-=-=-=-=-=-=-")
		print(user)
		newUrl = url + "posts/%s/posts/" % (user + "1000")

		response = requests.get(newUrl)
		print(response.text)

if option == 1:
	for user in users:
		for a in range(random.randint(0, 2)):
			newUrl = url + "posts/%s/posts/" % (user + "1000")

			response = requests.post(newUrl)
			print(response.text)

if option == 2:
	postIDList = list()

	for user in users:
		newUrl = url + "posts/%s/posts/" % (user + "1000")

		response = requests.get(newUrl)
		for post in response.json()["userPosts"]:
			postIDList.append(post["id"])

	for user in users:
		start = random.randint(0, len(postIDList))
		end   = random.randint(start, len(postIDList)) // 2

		for postID in postIDList[start:end]:
			newUrl = url + "posts/%s/watched/" % (user + "1000")

			clientRequest = {
				"postID": str(postID),
				"userRating": str(random.random())
			}
			response = requests.post(newUrl, clientRequest)
			print(response.text)



	# for user in users:
	# 	start = random.randint(0, len())
