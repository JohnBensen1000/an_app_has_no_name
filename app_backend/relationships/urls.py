from django.urls import path

from .views import *

urlpatterns = [
    path('<slug:uid>/following/',                   followings,     name='followings'),
    path('<slug:uid0>/following/<slug:uid1>/',      following,      name='following'),
    path('<slug:uid>/followers/',                   followers,      name='followers'),
    path('<slug:uid>/followers/new/',               new_followers,  name='new_followers'),
    path('<slug:uid>/blocked/',                     blocked,        name='blocked'),
    path('<slug:uid>/friends/',                     friends,        name='friends'),
]