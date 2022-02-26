import json

from django.test import TestCase, Client, client
from django.urls import reverse
from django.apps import apps

from .test import BaseTest

User          = apps.get_model("models", "User")
Preferences   = apps.get_model("models", "Preferences")
Profile       = apps.get_model("models", "Profile")
Blocked       = apps.get_model("models", "Blocked")
ChatMember    = apps.get_model("models", "ChatMember")
Chat          = apps.get_model("models", "Chat")
Post          = apps.get_model("models", "Post")
Following     = apps.get_model("models", "Following")

class TestBlocked(BaseTest):
    def setUp(self):
        self.cleint = Client()

    def test_block_new_user(self):
        '''
            User should be able to block another user. When this happens, the following relation
            between the first user and second user should be deleted. Additionally, any direct 
            messages between the two users should be deleted.
        '''
        user1 = self.create_user_object('user1', 'user1')
        user2 = self.create_user_object('user2', 'user2')

        Following.objects.create(follower=user2, creator=user1)
        Following.objects.create(follower=user1, creator=user2)

        chat1 = Chat.objects.create(chatID='13421', isDirectMessage=True)
        ChatMember.objects.create(isOwner=True, chat=chat1, member=user1)
        ChatMember.objects.create(isOwner=True, chat=chat1, member=user2)

        url      = reverse('blocked', kwargs={"uid": user1.uid})
        response = self.client.post(
            url,
            json.dumps({
                'uid': user2.uid
            }),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Blocked.objects.filter(user=user1, creator=user2).exists(), True)

        self.assertEqual(Chat.objects.count(), 0)
        self.assertEqual(Following.objects.filter(follower=user1, creator=user2).exists(), False)
        self.assertEqual(Following.objects.filter(follower=user2, creator=user1).exists(), True)

    def test_get_list_of_blocked_creators(self):
        '''
            A user should be able to get a list of all of the users that they are blocking.
        '''

        user1 = self.create_user_object('user1', 'user1')
        user2 = self.create_user_object('user2', 'user2')
        user3 = self.create_user_object('user3', 'user3')
        user4 = self.create_user_object('user4', 'user4')

        Blocked.objects.create(user=user1, creator=user2)
        Blocked.objects.create(user=user1, creator=user3)

        url      = reverse('blocked', kwargs={"uid": user1.uid})
        response = json.loads(self.client.get(url).content)

        self.assertEqual(len(response['blocked']), 2)
        self.assertEqual(response['blocked'][0]['uid'], user2.uid)
        self.assertEqual(response['blocked'][1]['uid'], user3.uid)

    def test_unblock_user(self):
        '''
            A user should be able to 'unblock' another user by deleted the blocked relationship 
            between the two users.
        '''
        user1 = self.create_user_object('user1', 'user1')
        user2 = self.create_user_object('user2', 'user2')

        Blocked.objects.create(
            user    = user1,
            creator = user2,
        )

        url = reverse("blocked_user", kwargs={"uid": user1.uid, "uid1": user2.uid})

        response = self.client.delete(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Blocked.objects.filter(user=user1, creator=user2).exists(), False)
