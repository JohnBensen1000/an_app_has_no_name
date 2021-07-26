import json

from django.test import TestCase, Client, client
from django.urls import reverse
from django.apps import apps

User        = apps.get_model("models", "User")
Preferences = apps.get_model("models", "Preferences")
Profile     = apps.get_model("models", "Profile")
Post        = apps.get_model("models", "Post")
Following   = apps.get_model("models", "Following")
WatchedBy   = apps.get_model("models", "WatchedBy")
Blocked     = apps.get_model("models", "Blocked")
Reported    = apps.get_model("models", "Reported")
Chat        = apps.get_model("models", "Chat")
ChatMember  = apps.get_model("models", "ChatMember")

class TestUser(TestCase):
    def setUp(self):
        self.client = Client()
        self.user   = self.create_user_object("test", "test")

    def create_user_object(self, userID, username):
        return User.objects.create(
            userID      = userID,
            email       = userID + '@gmail.com',
            username    = username,
            preferences = Preferences.objects.create(),
            profile     = Profile.objects.create(),
            uid         = userID + username
        )

    def test_checking_if_user_id_taken(self):
        userID1       = "test"
        url1          = reverse('userIdTaken')
        response1     = self.client.get(url1, {'userID': userID1})
        responseBody1 = json.loads(response1.content)

        userID2       = "test12345"
        url2          = reverse('userIdTaken')
        response2     = self.client.get(url2, {'userID': userID2})
        responseBody2 = json.loads(response2.content)

        self.assertEqual(response1.status_code, 200)
        self.assertEqual(response2.status_code, 200)

        self.assertTrue(responseBody1['isUserIdTaken'])
        self.assertFalse(responseBody2['isUserIdTaken'])

    def test_delete_account(self):
        '''
            When a user deletes their account, makes sure that all the direct messages they are
            in are also deleted.
        '''
        user2 = self.create_user_object("test2", "test2")
        chat  = Chat.objects.create(
            chatID          = "chatID",
            chatName        = "chatName",
            isDirectMessage = True
        )
        ChatMember.objects.create(
            member  = self.user,
            chat    = chat,
            isOwner = True
        )
        ChatMember.objects.create(
            member  = user2,
            chat    = chat,
            isOwner = True
        )

        url      = reverse("user", kwargs={'uid': self.user.uid})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(Chat.objects.count(), 0)
        self.assertEqual(ChatMember.objects.count(), 0)
        self.assertEqual(ChatMember.objects.filter(member=user2).count(), 0)