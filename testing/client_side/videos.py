import requests
import json

def create_video(url):
	url += "client_side/videos/create_new_video/"

	creatorID = input("What is your user ID? ")
	clientRequest = {
		"creatorID":creatorID
	}
	response = requests.post(url, clientRequest)
	print(response.text)