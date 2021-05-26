  
from django.urls import path

from .views import *

urlpatterns = [
    path('<slug:postID>/watched_list/', watched_list,  name='watched_list'),   
    path('<slug:uid>/',                 posts,         name='posts'),	   
    path('<slug:uid>/<slug:postID>/',   post,          name='post'),
]