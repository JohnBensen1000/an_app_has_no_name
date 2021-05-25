from django.urls import path

from .views import *

urlpatterns = [
    path('<slug:uid>/signedInStatus/',  signedInStatus,   name='signedInStatus'),
    path('deviceSignedInOn/',           deviceSignedInOn, name='deviceSignedInOn'),

]