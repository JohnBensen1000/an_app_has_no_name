from django.urls import path

from .views.users import *
from .views.posts import *
from .views.followings import *
from .views.followers import *
from .views.blocked import *
from .views.watched import *
from .views.feeds import *
from .views.chats import *
from .views.access import *
from .views.reports import *

urlpatterns = [
    path('users',                                       users,                  name="users"),
    path('users/<slug:uid>',                            user,                   name="user"),
    path('users/<slug:uid>/preferences',                user_preferences,       name="user_preferences"),
    path('posts/<slug:uid>',                            posts,                  name="posts"),
    path('posts/<slug:uid>/profile',                    profile,                name="profile"),
    path('posts/<slug:uid>/<slug:postID>',              post,                   name="post"),
    path('followings/<slug:uid>',                       followings,             name="followings"),
    path('followings/<slug:uid>/<slug:uid1>',           following,              name="following"),
    path('followers/<slug:uid>',                        followers,              name="followers"),
    path('followers/<slug:uid>/new',                    new_followers,          name="new_followers"),
    path('blocked/<slug:uid>',                          blocked,                name="blocked"),
    path('blocked/<slug:uid>/<slug:uid1>',              blocked_user,           name="blocked_user"),
    path('watched/<slug:postID>',                       watched,                name="watched"),
    path('feeds/recommendations',                       recommendations_feed,   name="recommendations_feed"),
    path('feeds/following',                             following_feed,         name="following_feed"),
    path('chats/<slug:uid>',                            chats,                  name="chats"),
    path('chats/<slug:uid>/<chatID>',                   chat,                   name="chat"),
    path('reports/<slug:uid>/post',                     report_post,            name="report_post"),
    path('reports/<slug:uid>/profile',                  report_profile,         name="report_profile"),
    path('reports/<slug:uid>/<slug:postID>/comment',    report_comment,         name="report_comment"),
    path('access',                                      access,                 name="access"),
]
