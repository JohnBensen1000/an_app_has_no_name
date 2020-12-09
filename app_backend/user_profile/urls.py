from django.urls import path

from . import views

urlpatterns = [
    path('create_new_user/', views.create_new_user, name='create_new_user'), 	# POST
    path('search_creators/', views.search_creators, name='search_creators'),	# GET
    path('start_following/', views.start_following, name='start_following'), 	# POST
    path('get_followings/',  views.get_followings,  name='get_followings'),		# GET
    path('get_followers/',   views.get_followers,   name='get_followers'), 		# GET
    path('become_friends/',  views.become_friends,  name='become_friends'), 	# POST
    path('get_friends/',     views.get_friends,     name='get_friends'), 		# GET
]