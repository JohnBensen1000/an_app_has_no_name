
from django.urls import path

from .views import *

urlpatterns = [
    path('',                search,   name="search"),
    path('new/',            new_user, name="new_user"),
    path('<slug:userID>/',  user,     name="user"),
    path('profile/',        profile,  name="profile"),

]