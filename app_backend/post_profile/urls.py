from django.urls import path

from .views import *

urlpatterns = [
    path('<slug:chatName>/',                        chat),              # POST
    path('<slug:userID>/posts/',				    posts),		        # GET, POST, (DELETE)
    path('<slug:userID>/recommendations/',          recommendations),   # GET
    path('<slug:userID>/following/',                following),         # GET
    path('<slug:userID>/watched/<int:postID>/',	    watched),	        # POST
]