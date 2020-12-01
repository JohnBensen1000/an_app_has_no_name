from django.urls import path

from . import views

urlpatterns = [
    path('', views.create_new_user, name='create_new_user'),
]