from django.urls import path

from .views import *

urlpatterns = [
    path('',    access,     name='access'),
]