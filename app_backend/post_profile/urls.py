from django.urls import path

from .views import *

urlpatterns = [
    path('<slug:userID>/posts/',	update_posts),		# GET, POST, (DELETE)
    path('<slug:userID>/watched/',	record_watched),	# POST
]