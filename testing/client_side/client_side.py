import requests
import json

# test files
import users
import videos

urls = ["http://127.0.0.1:8000/", "https://app-cloud-297304.uc.r.appspot.com/"] 


if __name__ == "__main__":
	print("Which environment are you performing this test in?")
	print("		[0] Development")
	print("		[1] Staging")
	print("		[2] Production")
	env = int(input("Environment: "))

	url = urls[env]

	print("What action do you want to take?")
	print("		[0] Create Account")
	print("		[1] Create Video")
	print("		[2] Find Creators")
	print("		[3] Start Following")
	print("		[4] Get Followings")
	print("		[5] Become Friends")
	print("		[6] Get Friends")

	func = int(input("Action: "))

	if func == 0: users.create_account(url)
	if func == 1: videos.create_video(url)
	if func == 2: users.find_creators(url)
	if func == 3: users.start_following(url)
	if func == 4: users.get_following(url)
	if func == 5: users.become_friends(url)
	if func == 6: users.get_friends(url)