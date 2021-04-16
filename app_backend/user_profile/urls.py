from django.urls import path

from .views import *

# HTTP methods in paranthesis are methods that will be supported in the 
# future but are not supported yet

urlpatterns = [
    path('search/<slug:searchString>/',  				creators),	                        # GET
    path('check/',                                      identifiers),                       
    path('<slug:userID>/',  							user),		                        # GET, POST, DELETE, (PUT)
    path('<slug:userID>/profile/',  					profile),		                    # GET, POST
    path('<slug:userID>/following/',                 	following_list),                    # GET
    path('<slug:userID>/following/<slug:creatorID>/', 	following),	                        # GET, POST, DELETE
    path('<slug:userID>/friends/',                		friends), 		                    # GET
    # path('<slug:userID>/friends/<slug:friendID>/', 		friend),	                    # DELETE, (GET), (POST)
]