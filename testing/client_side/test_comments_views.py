import random
import requests

url = "http://127.0.0.1:8000/"

print("What action do you want to take?")
print("		[0] Post a comment")
print("		[1] Get comments for post")
print("		[2] Delete post's comments")
option = int(input("Option: "))

users = ["John", "Laura", "Kishan", "Alex", "Andrew", "Tim", "Jake", "Tom", "Nick", "Collin"]

if option == 0:
	newUrl = url + "comments/%d/comments/%s/" % (1, users[0])
	requestJson = {
		"path": "",
		"comment": "I liked this post.",
	}
	response = requests.post(newUrl, requestJson)
	print(response.text)

	newUrl = url + "comments/%d/comments/%s/" % (1, users[1])
	requestJson = {
		"path": "/c/John0",
		"comment": "I liked this post.",
	}
	response = requests.post(newUrl, requestJson)
	print(response.text)

	newUrl = url + "comments/%d/comments/%s/" % (1, users[2])
	requestJson = {
		"path": "/c/John0",
		"comment": "I liked this post.",
	}
	response = requests.post(newUrl, requestJson)
	print(response.text)

	newUrl = url + "comments/%d/comments/%s/" % (1, users[3])
	requestJson = {
		"path": "/c/John0/c/Kishan0",
		"comment": "I liked this post.",
	}
	response = requests.post(newUrl, requestJson)
	print(response.text)

if option == 1:
	newUrl = url + "comments/%d/comments/" % (1)

	response = requests.get(newUrl)
	print(response.text)

if option == 2:
	newUrl = url + "comments/%d/comments/" % (1)

	response = requests.delete(newUrl)
	print(response.text)
