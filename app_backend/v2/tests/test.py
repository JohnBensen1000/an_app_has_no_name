import random

from django.test import TestCase, Client, client
from django.apps import apps

User        = apps.get_model("models", "User")
Preferences = apps.get_model("models", "Preferences")
Profile     = apps.get_model("models", "Profile")
User        = apps.get_model("models", "User")
Post        = apps.get_model("models", "Post")

class BaseTest(TestCase):        
    def create_user_object(self, userID, username):
        return User.objects.create(
            userID      = userID,
            email       = userID + '@gmail.com',
            username    = username,
            preferences = Preferences.objects.create(),
            profile     = Profile.objects.create(),
            uid         = userID + username
        )

    def create_post_object(self, user, postID='test13342'):
        return Post.objects.create(
            postID      = postID,
            downloadURL = 'download.com',
            isImage     = True,
            preferences = Preferences.objects.create(),
            creator     = user,
        )          