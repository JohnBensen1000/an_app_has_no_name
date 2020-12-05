import sys

from django.shortcuts import render
from demographics.models import Demographics
from user_profile.models import UserProfile
from video_profile.models import VideoProfile
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
# Create your views here.

@csrf_exempt
def create_new_video(request):
	try:
		videoProfile = request.POST

		creator   = UserProfile.objects.get(userID=videoProfile["creatorID"])
		videoDemo = Demographics()
		videoDemo.save()

		newVideo = VideoProfile(
			demographics = videoDemo,
			creator      = creator
		)
		newVideo.save()
		return HttpResponse()

	except:
		return HttpResponse(str(sys.exc_info()[0]))

if __name__ == "__main__":
	pass