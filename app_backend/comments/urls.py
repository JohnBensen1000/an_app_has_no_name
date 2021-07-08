from django.urls import path

from .views import *

urlpatterns = [
    path('<int:postID>/',           comments),    # GET, POST, (DELETE)
    path('<int:postID>/report/',    report),
]