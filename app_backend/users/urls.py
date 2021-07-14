from django.urls import path

from .views import *

urlpatterns = [
    path('',                        userIdTaken,        name='userIdTaken'),
    path('preferences/',            preferences,        name="preferences"),
    path('new/',                    new_user,           name="new_user"),
    path('<slug:uid>/',             user,               name="user"),
    path('<slug:uid>/search/',      search,             name="search"),
    path('<slug:uid>/preferences/', user_preferences,   name="user_preferences"),

]