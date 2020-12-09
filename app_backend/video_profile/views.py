import sys

from django.shortcuts import render
from demographics.models import Demographics
from user_profile.models import UserProfile
from video_profile.models import *
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
# Create your views here.

@csrf_exempt
def create_new_video(request):
	try:
		videoProfile = request.POST

		videoDemo = Demographics.objects.create()
		creator   = UserProfile.objects.get(userID=videoProfile["creator"])

		VideoProfile.objects.create(
			private      = False,
			demographics = videoDemo,
			creator      = creator,
		)
		return HttpResponse("Successfully created new video!")

	except:
		return HttpResponse(str(sys.exc_info()[0]))

@csrf_exempt
def record_watched_video(request):
	try:
		recordWatched = request.POST
		user          = UserProfile.objects.get(userID=recordWatched["user"])
		video         = VideoProfile.objects.get(videoID=recordWatched["videoID"])
		video.watchedBy.add(user)

		return HttpResponse("Successfully recorded that user watched a video.")

	except:
		return HttpResponse(str(sys.exc_info()[0]))

@csrf_exempt
def get_posted_videos(request):
	try:
		recordWatched = request.GET
		userProfile   = UserProfile.objects.get(userID=recordWatched["user"])
		postedVideos  = [video.id for video in VideoProfile.objects.filter(creator=userProfile)]

		return HttpResponse(postedVideos)

	except:
		return HttpResponse(str(sys.exc_info()[0]))



if __name__ == "__main__":
	pass