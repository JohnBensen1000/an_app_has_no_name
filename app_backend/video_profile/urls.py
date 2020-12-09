from django.urls import path

from . import views

urlpatterns = [
    path('create_new_video/',     views.create_new_video,     name='create_new_video'),		# POST
    path('record_watched_video/', views.record_watched_video, name='record_watched_video'), # POST
    path('get_posted_videos/',    views.get_posted_videos,    name='get_posted_videos'),  	# GET
]