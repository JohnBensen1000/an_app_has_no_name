from django.urls import path

from .views import *

urlpatterns = [
    path('<slug:uid>/',                         chats,      name='chats'),
    path('<slug:uid>/<slug:chatID>/',           chat,       name='chat'),
    path('<slug:uid>/<slug:chatID>/updated/',   updated,    name='updated'),
    path('<slug:uid>/<slug:chatID>/report/',    report,     name='report'),
    path('<slug:uid>/<slug:chatID>/members/',   members,    name='members'),
]