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

class TestFollowings(BaseTest):
    def setUp(self):
        self.user   = self.create_user_object('test', 'test')
        self.cleint = Client()

    def test_get_list_of_followings(self):
        '''
            Creates a couple of following relations between the user and other users.
            One of these other users is also following the user. Tests to see if the
            list of followings is correct. Also checks to see if the other user that is
            following the main user is considered a 'friend'.
        '''
        user1 = self.create_user_object('user1', 'user1')
        user2 = self.create_user_object('user2', 'user2')

        Following.objects.create(
            follower    = self.user,
            creator     = user1,
            newFollower = True, 
        )
        Following.objects.create(
            follower    = self.user,
            creator     = user2,
            newFollower = True, 
        )
        Following.objects.create(
            follower    = user2,
            creator     = self.user,
            newFollower = False, 
        )

        url            = reverse('followings', kwargs={'uid': self.user.uid})
        response       = self.client.get(url)
        responseBody   = json.loads(response.content)
        followingsList = responseBody["followings"]

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(followingsList), 2)

        self.assertEqual(followingsList[0]["user"]["userID"], 'user1')
        self.assertEqual(followingsList[1]["user"]["userID"], 'user2')
        self.assertEqual(followingsList[0]["isFriend"], False)
        self.assertEqual(followingsList[1]["isFriend"], True)

    def test_start_following_user(self):
        '''
            Tests to see if a user can start following another user.
        '''
        user3 = self.create_user_object('user3', 'user3')

        url      = reverse('followings', kwargs={'uid': self.user.uid})
        response = self.client.post(
            url, 
            json.dumps({
                "uid":  user3.uid,
            }),
            content_type='application/json'
        )

        following = Following.objects.filter(follower=self.user, creator=user3).first()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(following.follower.uid, self.user.uid)
        self.assertEqual(following.newFollower, True)

    def test_start_following_when_creator_followers_user(self):
        '''
            When a user starts following a creator, and the creator is already following the user,
            then a new Following entity should be created with newFollower set to False. 
        '''
        creator = self.create_user_object('creator', 'creator')
        Following.objects.create(
            follower    = creator,
            creator     = self.user,
        )

        url      = reverse('followings', kwargs={'uid': self.user.uid})
        response = self.client.post(
            url, 
            json.dumps({
                "uid":  creator.uid,
            }),
            content_type='application/json'
        )

        following = Following.objects.filter(follower=self.user, creator=creator).first()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(following.follower.uid, self.user.uid)
        self.assertEqual(following.newFollower, False)

    def test_get_if_user_following_creator(self):
        '''
            Tests getting the following relationship between two users.
        '''
        user1 = self.create_user_object('user1', 'user1')
        user2 = self.create_user_object('user2', 'user2')
        Following.objects.create(
            follower = self.user,
            creator  = user1,
        )

        url1      = reverse('following', kwargs={'uid': self.user.uid, 'uid1': user1.uid})
        response1 = json.loads(self.client.get(url1).content)
        url2      = reverse('following', kwargs={'uid': self.user.uid, 'uid1': user2.uid})
        response2 = json.loads(self.client.get(url2).content)

        self.assertTrue(response1['isFollowing'])
        self.assertFalse(response2['isFollowing'])

    def test_update_new_follower_to_false(self):
        '''
            When a user decides to not follow back a creator, then the 'newFollower' field in the
            creator->user following relationship should be set to false.
        '''
        user1 = self.create_user_object('user1', 'user1')
        Following.objects.create(
            follower = user1,
            creator  = self.user,
        )

        url1      = reverse('following', kwargs={'uid': user1.uid, 'uid1': self.user.uid})
        response  = self.client.put(url1, json.dumps({}), content_type='application/json')

        following = Following.objects.filter(follower=user1, creator=self.user).first()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(following.newFollower, False)

    def test_stop_following(self):
        '''
            When a user stops following a creator, the user-creator following relationship should be
            deleted. Also, any direct messages between these two users should be deleted. An chats that
            are not direct messages that have both of these users should not be deleted. The creator->user
            following relationship should also not be deleted.
        '''
        user1 = self.create_user_object('user1', 'user1')
        user2 = self.create_user_object('user2', 'user2')

        Following.objects.create(follower=user2, creator=user1)
        Following.objects.create(follower=user1, creator=user2)

        chat1 = Chat.objects.create(isDirectMessage=True)
        ChatMember.objects.create(isOwner=True, chat=chat1, member=user1)
        ChatMember.objects.create(isOwner=True, chat=chat1, member=user2)

        chat2 = Chat.objects.create(isDirectMessage=False)
        ChatMember.objects.create(isOwner=True, chat=chat2, member=user1)
        ChatMember.objects.create(isOwner=True, chat=chat2, member=user2)

        url      = reverse('following', kwargs={'uid': user1.uid, 'uid1': user2.uid})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Following.objects.filter(follower=user1, creator=user2).count(), 0)
        self.assertEqual(Following.objects.filter(follower=user2, creator=user1).count(), 1)

        self.assertEqual(Chat.objects.count(), 1)
        self.assertFalse(Chat.objects.filter(chatID=chat1.chatID).exists())
        self.assertTrue(Chat.objects.filter(chatID=chat2.chatID).exists())

