from django.urls import path

from .views import *

# HTTP methods in paranthesis are methods that will be supported in the 
# future but are not supported yet

urlpatterns = [
    path('',    authentication),
]