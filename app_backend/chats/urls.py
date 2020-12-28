from django.urls import path

from .views import *

urlpatterns = [
    path('<slug:userID>/',                  						all_chats),		 # GET
    path('<slug:userID>/direct/<slug:recieverID>/', 				direct_chat),	 # GET, POST, DELETE
    path('<slug:userID>/group/<slug:groupchatID>/', 				group_chat),	 # GET, POST, DELETE
    path('<slug:userID>/group/<slug:groupchatID>/<slug:memberID>/',	group_member), 	 # POST, DELETE
]