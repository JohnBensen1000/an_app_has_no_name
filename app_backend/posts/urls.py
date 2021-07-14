  
from django.urls import path

from .views import *

urlpatterns = [
    path('<slug:postID>/watched_list/',         watched_list,  name='watched_list'),   
    path('<slug:uid>/',                         posts,         name='posts'),	 
    path('<slug:uid>/profile/',                 profile,       name='profile'),
    path('<slug:uid>/reports/',                 reports,       name='reports'), 
    path('<slug:uid>/<slug:postID>/',           post,          name='post'),
]