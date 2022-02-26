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

class TestChats(BaseTest):
    def setUp(self):
        self.user   = self.create_user_object('test', 'test')
        self.client = Client()

    def test_create_direct_message(self):
        '''
            The user could create a direct message with another user. Tests to see if
            the new chat is created and is a direct message.
        '''

        user1 = self.create_user_object('user1', 'user1')

        url      = reverse('chats', kwargs={'uid': self.user.uid})
        response = self.client.post(
            url,
            data=json.dumps({
                'isDirectMessage': True,
                'members': [user1.uid],
                'chatName': 'chatName'
            }),
            content_type='application/json',
        )

        chat = Chat.objects.first()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Chat.objects.count(), 1)
        self.assertEqual(ChatMember.objects.count(), 2)
        self.assertEqual(chat.isDirectMessage, True)

    def test_get_all_chats(self):
        '''
            The user could get all the chats that they are in.
        '''
        chat1 = Chat.objects.create(
            chatName = "this is my first chat",
        )
        chat2 = Chat.objects.create(
            chatName = "this is my second chat",
        )
        chat3 = Chat.objects.create(
            chatName = "this is my third chat",
        )

        user1 = self.create_user_object('user1', 'user1')
        user2 = self.create_user_object('user2', 'user2')

        ChatMember.objects.create(
            member=self.user,
            chat=chat1,
            isOwner=False,
        )
        ChatMember.objects.create(
            member=user1,
            chat=chat1,
            isOwner=False,
        )
        ChatMember.objects.create(
            member=user2,
            chat=chat1,
            isOwner=False,
        )

        ChatMember.objects.create(
            member=self.user,
            chat=chat2,
            isOwner=False,
        )
        ChatMember.objects.create(
            member=self.user,
            chat=chat3,
            isOwner=True,
        )

        url          = reverse('chats', kwargs={'uid': self.user.uid})
        response     = self.client.get(url)
        responseBody = json.loads(response.content)
        chatList     = responseBody['chats']

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(chatList), 3)
