from django.urls import path

from .views import *

urlpatterns = [
    path('<slug:userID>/',                  				all_chats),		 	# GET
    path('<slug:userID>/new_direct/', 						new_direct_chat),	# POST
    path('<slug:userID>/new_group/', 						new_group_chat), 	# POST
    path('<slug:userID>/<slug:chatID>/', 					chat),	 			# GET, POST, (DELETE)
    path('<slug:userID>/<slug:chatID>/<slug:memberID>/',	group_member), 	 	# POST, DELETE, (GET)
]