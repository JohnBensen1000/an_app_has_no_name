from django.urls import path

from .views import *

# HTTP methods in paranthesis are methods that will be supported in the 
# future but are not supported yet

urlpatterns = [
    path('new_user/',      								new_user), 	        # GET, POST
    path('search/<slug:searchString>/',  				search_creators),	# GET
    path('<slug:userID>/',  							user),		        # DELETE, GET, PUT, (POST)
    path('<slug:userID>/following/',                 	following),	        # GET
    path('<slug:userID>/following/new/',             	start_following), 	# POST
    path('<slug:userID>/following/<slug:creatorID>/', 	update_following),	# DELETE, (GET), (POST)
    path('<slug:userID>/friends/',                		get_friends), 		# GET
    path('<slug:userID>/friends/new/',            		become_friends), 	# POST
    path('<slug:userID>/friends/<slug:friendID>/', 		update_friendship),	# DELETE, (GET), (POST)
]