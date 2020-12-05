from django.urls import path

from . import views

urlpatterns = [
    path('create_new_video/', views.create_new_video, name='create_new_video'),
]