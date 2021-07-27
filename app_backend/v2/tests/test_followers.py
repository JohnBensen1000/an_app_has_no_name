import json

from django.test import TestCase, Client, client
from django.urls import reverse
from django.apps import apps

from test import BaseTest

User          = apps.get_model("models", "User")
Preferences   = apps.get_model("models", "Preferences")
Profile       = apps.get_model("models", "Profile")
Blocked       = apps.get_model("models", "Blocked")
ChatMember    = apps.get_model("models", "ChatMember")
Chat          = apps.get_model("models", "Chat")
Post          = apps.get_model("models", "Post")
Following     = apps.get_model("models", "Following")

class TestFollowers(BaseTest):
    def setUp(self):
        self.user   = self.create_user_object('test', 'test')
        self.cleint = Client()

    def test_get_followers(self):
        '''
            Should return a list of all users that are following a user.
        '''
        user1 = self.create_user_object('user1', 'user1')
        user2 = self.create_user_object('user2', 'user2')
        user3 = self.create_user_object('user3', 'user3')
        user4 = self.create_user_object('user4', 'user4')

        Following.objects.create(follower=user2, creator=user1)
        Following.objects.create(follower=user4, creator=user1)

        url          = reverse('followers', kwargs={'uid': user1.uid})
        response     = self.client.get(url)
        responseBody = json.loads(response.content)
        
        self.assertEqual(response.status_code, 200) 
        self.assertEqual(len(responseBody["followers"]), 2)
        self.assertEqual(responseBody["followers"][0]['uid'], user2.uid)
        self.assertEqual(responseBody["followers"][1]['uid'], user4.uid)

    def test_get_new_followers(self):
        '''
            Should only return a list of new followers.
        '''
        user1 = self.create_user_object('user1', 'user1')
        user2 = self.create_user_object('user2', 'user2')
        user3 = self.create_user_object('user3', 'user3')
        user4 = self.create_user_object('user4', 'user4')

        Following.objects.create(follower=user2, creator=user1, newFollower=True)
        Following.objects.create(follower=user4, creator=user1, newFollower=False)

        url          = reverse('new_followers', kwargs={'uid': user1.uid})
        response     = self.client.get(url)
        responseBody = json.loads(response.content)
        
        self.assertEqual(response.status_code, 200) 
        self.assertEqual(responseBody["followerList"][0]['uid'], user2.uid)
        self.assertEqual(len(responseBody["followerList"]), 1)