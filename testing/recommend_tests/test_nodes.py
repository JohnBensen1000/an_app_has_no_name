import requests
import json

url = "http://127.0.0.1:8000/"

print("What do you want to do?")
print("		[0] create new users")
print("		[1] create friendship")

option = int(input("Option: "))

if option == 0:
	url += "user/new_user/"

	requestJson = {
		"userID":"Andrew",
		"embedding":str([1, 0, 1, 1, 0])
	}

	response = requests.post(url, requestJson)
	print(response.text)

if option == 1:
	url += "user/friends/"

	requestJson = {
		"friendID_0":"Laura",
		"friendID_1":"John"
	}
	response = requests.post(url, requestJson)
	print(response.text)