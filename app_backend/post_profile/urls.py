from django.urls import path

from .views import *

urlpatterns = [
    path('<slug:userID>/posts/',				    posts),		        # GET, POST, (DELETE)
    path('<slug:userID>/recommendations/',          recommended_posts), # GET
    path('<slug:userID>/following/new/',            following_posts),   # GET
    path('<slug:userID>/watched/<int:postID>/',	    watched),	        # POST
]