import requests
import json

print("Which environment are you performing this test in?")
print("		[0] Development")
print("		[1] Staging")
print("		[2] Production")
env = int(input("Environment: "))

url = ""
if env == 0:
	url = "http://127.0.0.1:8000/client_side/create_new_user/"
elif env == 1:
	url = "https://python-backend-demo-294820.uc.r.appspot.com/client_side/create_new_user/"
else:
	print("Invalid input.")

print("url", url)


demographics      = [1 if a % 4 == 1 else 0 for a in range(17)]
userID            = "user_id_1"
preferredLanguage = "English"
username          = "tim"

clientRequest = {
	"demographics":str(demographics),
	"userID":userID,
	"preferredLanguage":preferredLanguage,
	"username":username
}

response = requests.post(url, clientRequest)
print(response.text)