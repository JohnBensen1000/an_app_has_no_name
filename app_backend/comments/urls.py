from django.urls import path

from .views import *

urlpatterns = [
    path('<int:postID>/comments/',                  access_comment),  	# GET, DELETE
    path('<int:postID>/comments/<slug:userID>/',    post_comment),  	# POST, (GET), (PUT), (DELETE)
]