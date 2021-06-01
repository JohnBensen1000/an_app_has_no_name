from django.urls import path

from .views import *

urlpatterns = [
    path('<slug:uid>/recommendations/', recommendations, name="recommendations"),
    path('<slug:uid>/following/',       following,       name="following"),

]