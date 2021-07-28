from django.urls import path

from .views import *

urlpatterns = [
    path('access/',    access,     name='access'),

    path('authentication/<slug:uid>/signedInStatus/',  signedInStatus,   name='signedInStatus'),
    path('authentication/deviceSignedInOn/',           deviceSignedInOn, name='deviceSignedInOn'),

    path('chats/<slug:uid>/',                         chats,      name='chats'),
    path('chats/<slug:uid>/<slug:chatID>/',           chat,       name='chat'),
    path('chats/<slug:uid>/<slug:chatID>/updated/',   updated,    name='updated'),
    path('chats/<slug:uid>/<slug:chatID>/report/',    report,     name='report'),
    path('chats/<slug:uid>/<slug:chatID>/members/',   members,    name='members'),

    path('comments/<int:postID>/',           comments),    
    path('comments/<int:postID>/report/',    report),

    path('new_content/<slug:uid>/recommendations/', recommendations,    name="recommendations"),
    path('new_content/<slug:uid>/following/',       following_content,  name="following_content"),

    path('posts/<slug:postID>/watched_list/',         watched_list,       name='watched_list'),   
    path('posts/<slug:uid>/',                         posts,              name='posts'),	 
    path('posts/<slug:uid>/profile/',                 profile,            name='profile'),
    path('posts/<slug:uid>/reports/',                 reports,            name='reports'), 
    path('posts/<slug:uid>/reports/profile/',         reports_profile,    name='reports_profile'), 
    path('posts/<slug:uid>/<slug:postID>/',           post,               name='post'),

    path('relationships/<slug:uid>/following/',                   followings,     name='followings'),
    path('relationships/<slug:uid0>/following/<slug:uid1>/',      following,      name='following'),
    path('relationships/<slug:uid>/followers/',                   followers,      name='followers'),
    path('relationships/<slug:uid>/followers/new/',               new_followers,  name='new_followers'),
    path('relationships/<slug:uid>/blocked/',                     blocked,        name='blocked'),
    path('relationships/<slug:uid>/blocked/<slug:creator_uid>/',  blocked_user,   name='blocked_user'),
    path('relationships/<slug:uid>/friends/',                     friends,        name='friends'),

    path('users/',                        userIdTaken,        name='userIdTaken'),
    path('users/preferences/',            preferences,        name="preferences"),
    path('users/new/',                    new_user,           name="new_user"),
    path('users/<slug:uid>/',             user,               name="user"),
    path('users/<slug:uid>/search/',      search,             name="search"),
    path('users/<slug:uid>/preferences/', user_preferences,   name="user_preferences"),

]