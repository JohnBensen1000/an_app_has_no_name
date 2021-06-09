from django.urls import path

from .views import *

urlpatterns = [
    path('',                        search,             name="search"),
    path('preferences/',            preferences,        name="preferences"),
    path('new/',                    new_user,           name="new_user"),
    path('<slug:uid>/',             user,               name="user"),
    path('<slug:uid>/preferences/', user_preferences,   name="user_preferences"),

]