import requests
import json

users = ["John", "Laura", "Kishan", "Alex", "Andrew", "Tim", "Jake", "Tom", "Nick", "Collin"]

def create_new_video(url):
	url += "client_side/videos/create_new_video/"

	for a in range(3):
		clientRequest = {
			"creator":users[0] + "1000"
		}
		response = requests.post(url, clientRequest)
		print(response.text)

def record_watched_video(url):
	url += "client_side/videos/record_watched_video/"

	for user in users[1: ]:
		clientRequest = {
			"user":user + "1000",
			"videoID":1
		}
		response = requests.post(url, clientRequest)
		print(response.text)