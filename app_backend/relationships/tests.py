import json
import sys

from django.test import TestCase, Client, client
from django.urls import reverse
from django.apps import apps

User          = apps.get_model("models", "User")
Preferences   = apps.get_model("models", "Preferences")
Profile       = apps.get_model("models", "Profile")
Relationships = apps.get_model("models", "Relationships")
ChatMember    = apps.get_model("models", "ChatMember")
Chat          = apps.get_model("models", "Chat")

class FollowingsTest(TestCase):
    def setUp(self):
        self.userID   = "John"
        self.username = "John Bensen"
        self.uid      = '12345'
    
        self.client = Client()
        self.url    = reverse('followings', kwargs={'uid': self.uid})

        self.user = User.objects.create(
            userID   = self.userID,
            email    = self.userID + "@gmail.com",
            phone    = self.userID + "12345",
            username = self.username,
            uid      = self.uid,
            preferences = Preferences.objects.create(),
            profile     = Profile.objects.create(),
        ) 

        self.user1 = User.objects.create(
            userID   = 'jake',
            email    = "jake@gmail.com",
            phone    = "12345",
            username = 'jakelessman',
            uid      = '123456',
            preferences = Preferences.objects.create(),
            profile     = Profile.objects.create(),
        )
        self.user2 = User.objects.create(
            userID   = 'andrew',
            email    = "jake11@gmail.com",
            phone    = "1232334245",
            username = 'jakelessman',
            uid      = '1212',
            preferences = Preferences.objects.create(),
            profile     = Profile.objects.create(),
        )

    def test_get_list_of_followings(self):
        Relationships.objects.create(
            follower    = self.user,
            creator     = self.user1,
            newFollower = True, 
        )
        Relationships.objects.create(
            follower    = self.user,
            creator     = self.user2,
            newFollower = True, 
        )
        Relationships.objects.create(
            follower    = self.user2,
            creator     = self.user,
            newFollower = False, 
        )

        response       = self.client.get(self.url)
        responseBody   = json.loads(response.content)
        followingsList = responseBody["followings"]

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(followingsList), 2)

        self.assertEqual(followingsList[0]["user"]["userID"], 'jake')
        self.assertEqual(followingsList[1]["user"]["userID"], 'andrew')
        self.assertEqual(followingsList[0]["isFriend"], False)
        self.assertEqual(followingsList[1]["isFriend"], True)

    def test_start_following(self):
        Relationships.objects.create(
            follower    = self.user2,
            creator     = self.user,
            newFollower = False, 
        )

        response1 = self.client.post(
            self.url, 
            json.dumps({
                'uid': self.user1.uid
            }),
            content_type='application/json'
        )
        response2 = self.client.post(
            self.url, 
            json.dumps({
                'uid': self.user2.uid
            }),
            content_type='application/json'
        )

        relation1 = Relationships.objects.get(follower=self.user, creator=self.user1)
        relation2 = Relationships.objects.get(follower=self.user, creator=self.user2)

        self.assertEqual(ChatMember.objects.filter(member=self.user)[0].chat, ChatMember.objects.filter(member=self.user2)[0].chat)

        self.assertEqual(response1.status_code, 201)
        self.assertEqual(response2.status_code, 201)

        self.assertEqual(relation1.newFollower, True)
        self.assertEqual(relation2.newFollower, False)


class FollowingTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create(
            userID   = 'jake',
            email    = "jake@gmail.com",
            phone    = "12345",
            username = 'jakelessman',
            uid      = '123456',
            preferences = Preferences.objects.create(),
            profile     = Profile.objects.create(),
        )
        self.user2 = User.objects.create(
            userID   = 'andrew',
            email    = "jake11@gmail.com",
            phone    = "1232334245",
            username = 'jakelessman',
            uid      = '1212',
            preferences = Preferences.objects.create(),
            profile     = Profile.objects.create(),
        )

        Relationships.objects.create(
            follower    = self.user1,
            creator     = self.user2,
            newFollower = True, 
        )

        self.client = Client()
        self.url1   = reverse('following', kwargs={'uid0': self.user1.uid, 'uid1': self.user2.uid})
        self.url2   = reverse('following', kwargs={'uid0': self.user2.uid, 'uid1': self.user1.uid})


    def test_get_following(self):
        response1 = self.client.get(self.url1)
        response2 = self.client.get(self.url2)

        isFollowing1 = json.loads(response1.content)["isFollowing"]
        isFollowing2 = json.loads(response2.content)["isFollowing"]

        self.assertEqual(isFollowing1, True)
        self.assertEqual(isFollowing2, False)

    def test_follow_back(self):
        response = self.client.post(
            self.url1,
            json.dumps({
                'followBack': True
            }),
            content_type='application/json'
        )

        following          = Relationships.objects.get(follower=self.user1, creator=self.user2)
        newFollowingExists = Relationships.objects.filter(follower=self.user2, creator=self.user1).exists()

        self.assertEqual(ChatMember.objects.filter(member=self.user1)[0].chat, ChatMember.objects.filter(member=self.user2)[0].chat)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(following.newFollower, False)
        self.assertEqual(newFollowingExists, True)

    def test_dont_follow_back(self):
        response = self.client.post(
            self.url1,
            json.dumps({
                'followBack': False
            }),
            content_type='application/json'
        )

        following = Relationships.objects.get(follower=self.user1, creator=self.user2)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(following.newFollower, False)

    def test_delete_friendship(self):
        Relationships.objects.create(
            follower    = self.user2,
            creator     = self.user1,
            newFollower = True, 
        )
        chat = Chat.objects.create(
            isDirectMessage=True
        )
        ChatMember.objects.create(
            isOwner = True,
            chat    = chat,
            member  = self.user1
        )
        ChatMember.objects.create(
            isOwner = True,
            chat    = chat,
            member  = self.user2
        )

        response = self.client.delete(
            self.url1,
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Chat.objects.count(), 0)
        self.assertEqual(ChatMember.objects.count(), 0)


class FollowersTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create(
            userID   = 'jake',
            email    = "jake@gmail.com",
            phone    = "12345",
            username = 'jakelessman',
            uid      = '123456',
            preferences = Preferences.objects.create(),
            profile     = Profile.objects.create(),
        )
        self.user2 = User.objects.create(
            userID   = 'andrew',
            email    = "jake11@gmail.com",
            phone    = "1232334245",
            username = 'jakelessman',
            uid      = '1212',
            preferences = Preferences.objects.create(),
            profile     = Profile.objects.create(),
        )
        self.user3 = User.objects.create(
            userID   = 'alex',
            email    = "jake111@gmail.com",
            phone    = "123212334245",
            username = 'jakelessman',
            uid      = '12121',
            preferences = Preferences.objects.create(),
            profile     = Profile.objects.create(),
        )

        Relationships.objects.create(
            follower    = self.user2,
            creator     = self.user1,
            newFollower = True, 
        )
        Relationships.objects.create(
            follower    = self.user3,
            creator     = self.user1,
            newFollower = False, 
        )

        self.client = Client()
        self.url   = reverse('followers', kwargs={'uid': self.user1.uid})

    def test_get_followers(self):
        response     = self.client.get(self.url)
        responseBody = json.loads(response.content)
        
        self.assertEqual(response.status_code, 200) 
        self.assertEqual(responseBody["followerList"][0]['uid'], self.user2.uid)
        self.assertEqual(responseBody["followerList"][1]['uid'], self.user3.uid)

class NewFollowersTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create(
            userID   = 'jake',
            email    = "jake@gmail.com",
            phone    = "12345",
            username = 'jakelessman',
            uid      = '123456',
            preferences = Preferences.objects.create(),
            profile     = Profile.objects.create(),
        )
        self.user2 = User.objects.create(
            userID   = 'andrew',
            email    = "jake11@gmail.com",
            phone    = "1232334245",
            username = 'jakelessman',
            uid      = '1212',
            preferences = Preferences.objects.create(),
            profile     = Profile.objects.create(),
        )
        self.user3 = User.objects.create(
            userID   = 'alex',
            email    = "jake111@gmail.com",
            phone    = "123212334245",
            username = 'jakelessman',
            uid      = '12121',
            preferences = Preferences.objects.create(),
            profile     = Profile.objects.create(),
        )

        Relationships.objects.create(
            follower    = self.user2,
            creator     = self.user1,
            newFollower = True, 
        )
        Relationships.objects.create(
            follower    = self.user3,
            creator     = self.user1,
            newFollower = False, 
        )

        self.client = Client()
        self.url   = reverse('new_followers', kwargs={'uid': self.user1.uid})

    def test_get_followers(self):
        response     = self.client.get(self.url)
        responseBody = json.loads(response.content)
        
        self.assertEqual(response.status_code, 200) 
        self.assertEqual(responseBody["followerList"][0]['uid'], self.user2.uid)
        self.assertEqual(len(responseBody["followerList"]), 1)

class FriendsTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create(
            userID   = 'jake',
            email    = "jake@gmail.com",
            phone    = "12345",
            username = 'jakelessman',
            uid      = '123456',
            preferences = Preferences.objects.create(),
            profile     = Profile.objects.create(),
        )
        self.user2 = User.objects.create(
            userID   = 'andrew',
            email    = "jake11@gmail.com",
            phone    = "1232334245",
            username = 'jakelessman',
            uid      = '1212',
            preferences = Preferences.objects.create(),
            profile     = Profile.objects.create(),
        )
        self.user3 = User.objects.create(
            userID   = 'alex',
            email    = "jake111@gmail.com",
            phone    = "123212334245",
            username = 'jakelessman',
            uid      = '12121',
            preferences = Preferences.objects.create(),
            profile     = Profile.objects.create(),
        )

        Relationships.objects.create(
            follower    = self.user2,
            creator     = self.user1,
            newFollower = True, 
        )
        Relationships.objects.create(
            follower    = self.user3,
            creator     = self.user1,
            newFollower = False, 
        )
        Relationships.objects.create(
            follower    = self.user1,
            creator     = self.user3,
            newFollower = False, 
        )

        self.client = Client()
        self.url   = reverse('friends', kwargs={'uid': self.user1.uid})

    def test_get_followers(self):
        response     = self.client.get(self.url)
        responseBody = json.loads(response.content)
        
        self.assertEqual(response.status_code, 200) 
        self.assertEqual(responseBody["friendsList"][0]['uid'], self.user3.uid)
        self.assertEqual(len(responseBody["friendsList"]), 1)