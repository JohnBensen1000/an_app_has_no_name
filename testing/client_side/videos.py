import requests
import json
import random

users = ["John", "Laura", "Kishan", "Alex", "Andrew", "Tim", "Jake", "Tom", "Nick", "Collin"]

def create_new_video(url):
	url += "client_side/videos/create_new_video/"

	for user in users[1: ]:
		for a in range(random.randrange(5)):
			clientRequest = {
				"creator":user + "1000"
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

def get_posted_videos(url):
	url += "client_side/videos/get_posted_videos/"

	for user in users:
		clientRequest = {
			"creator":user + "1000" 
		}
		response = requests.get(url, clientRequest)
		print(response.text)