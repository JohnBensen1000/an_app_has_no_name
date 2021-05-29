import json
import sys

from django.test import TestCase, Client, client
from django.urls import reverse
from django.apps import apps
from django.core.files.uploadedfile import SimpleUploadedFile

User          = apps.get_model("models", "User")
Preferences   = apps.get_model("models", "Preferences")
Profile       = apps.get_model("models", "Profile")
Relationships = apps.get_model("models", "Relationships")
ChatMember    = apps.get_model("models", "ChatMember")
Chat          = apps.get_model("models", "Chat")

class ChatsTest(TestCase):
    def setUp(self):
        self.userID   = "John"
        self.username = "John Bensen"
        self.uid      = '12345'
    
        self.client = Client()
        self.url    = reverse('chats', kwargs={'uid': self.uid})

        self.user = User.objects.create(
            userID   = self.userID,
            email    = self.userID + "@gmail.com",
            phone    = self.userID + "12345",
            username = self.username,
            uid      = self.uid,
            preferences = Preferences.objects.create(),
            profile     = Profile.objects.create(),
        )

    def test_get_chats(self):
        chat1 = Chat.objects.create(
            chatName = "this is my first chat",
        )
        chat2 = Chat.objects.create(
            chatName = "this is my second chat",
        )
        chat3 = Chat.objects.create(
            chatName = "this is my third chat",
        )

        ChatMember.objects.create(
            member=self.user,
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

        response     = self.client.get(self.url)
        responseBody = json.loads(response.content)
        chatList     = responseBody['chatList']

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(chatList), 3)
        self.assertEqual(chatList[0]['chatID'], chat1.chatID)
        self.assertEqual(chatList[1]['chatID'], chat2.chatID)
        self.assertEqual(chatList[2]['chatID'], chat3.chatID)

    def test_create_new_chat(self):
        chatName = 'newChatName'

        response = self.client.post(
            self.url,
            json.dumps({
                'chatName': chatName,
            }),
            content_type='application/json'
        )
        chatMember = ChatMember.objects.filter(member=self.user)
        chat       = Chat.objects.first()

        self.assertEqual(response.status_code, 201)
        self.assertEqual(chatMember[0].chat, chat)
        self.assertEqual(chat.chatName, chatName)
        self.assertEqual(chatMember[0].isOwner, True)

class ChatTest(TestCase):
    def setUp(self):
        self.userID   = "UNIT_TEST"
        self.username = "John Bensen"
        self.uid      = 'UNIT_TEST'

        self.user = User.objects.create(
            userID   = self.userID,
            email    = self.userID + "@gmail.com",
            phone    = self.userID + "12345",
            username = self.username,
            uid      = self.uid,
            preferences = Preferences.objects.create(),
            profile     = Profile.objects.create(),
        )

        self.chat = Chat.objects.create(
            chatName = "UNIT_TEST_chat_name",
        )
        ChatMember.objects.create(
            member  = self.user,
            isOwner = True,
            chat    = self.chat 
        )

        self.client = Client()
        self.url    = reverse('chat', kwargs={'uid': self.uid, 'chatID': self.chat.chatID})

    def test_post_chat_text(self):
        response = self.client.post(
            self.url,
            json.dumps({
                'isPost': False,
                'text':   'Hello World!'
            }),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 201)
        
    def test_post_chat_post(self):
        file = SimpleUploadedFile('test.png', b'this is text, not an image')

        requestJson = json.dumps({
            'isPost':   True,
            'isImage':  True
        })
        form = {
            'media': file,
            'json':  requestJson,
        }
        response = self.client.post(self.url, data=form)

        self.assertEqual(response.status_code, 201)

    def test_chat_delete(self):
        response = self.client.delete(self.url)

        chatMemberExists = ChatMember.objects.filter(member=self.user, chat=self.chat).exists()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(chatMemberExists, False)

    def test_direct_message_delete(self):
        user1 = User.objects.create(
            userID   = 'Unit_test_id',
            email    = "Unit_test_id@gmail.com",
            phone    = "12345",
            username = 'test',
            uid      = '12345',
            preferences = Preferences.objects.create(),
            profile     = Profile.objects.create(),
        )
        chat = Chat.objects.create(
            chatName='test',
            isDirectMessage=True
        )
        ChatMember.objects.create(
            member=self.user,
            chat=chat,
            isOwner=True
        )
        ChatMember.objects.create(
            member=user1,
            chat=chat,
            isOwner=True
        )

        chatID = chat.chatID

        url      = reverse('chat', kwargs={'uid': self.uid, 'chatID': chat.chatID})
        response = self.client.delete(url)

        chatMemberExists1 = ChatMember.objects.filter(member=self.user, chat=chat).exists()
        chatMemberExists2 = ChatMember.objects.filter(member=user1, chat=chat).exists()
        chatExists        = Chat.objects.filter(chatID=chatID).exists()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(chatMemberExists1, False)
        self.assertEqual(chatMemberExists2, False)
        self.assertEqual(chatExists, False)

class MembersTest(TestCase):
    def setUp(self):
        self.userID   = "UNIT_TEST"
        self.username = "John Bensen"
        self.uid1     = 'UNIT_TEST'
        self.uid2     = 'uid2'
        self.uid3     = 'uide'

        self.user1 = User.objects.create(
            userID   = self.userID,
            email    = self.userID + "@gmail.com",
            phone    = self.userID + "12345",
            username = self.username,
            uid      = self.uid1,
            preferences = Preferences.objects.create(),
            profile     = Profile.objects.create(),
        )
        self.user2 = User.objects.create(
            userID   = 'self.userID',
            email    = 'test@gmail.com',
            phone    = "12345",
            username = 'self.username',
            uid      = self.uid2,
            preferences = Preferences.objects.create(),
            profile     = Profile.objects.create(),
        )
        self.user3 = User.objects.create(
            userID   = 'self.userID1',
            email    = "test1@gmail.com",
            phone    = "test212345",
            username = 'self.username',
            uid      = self.uid3,
            preferences = Preferences.objects.create(),
            profile     = Profile.objects.create(),
        )

        self.chat = Chat.objects.create(
            chatName = "UNIT_TEST_chat_name",
        )
        ChatMember.objects.create(
            member  = self.user1,
            isOwner = True,
            chat    = self.chat 
        )
        ChatMember.objects.create(
            member  = self.user2,
            isOwner = False,
            chat    = self.chat 
        )

        self.client = Client()
        self.url    = reverse('members', kwargs={'uid': self.uid1, 'chatID': self.chat.chatID})

    def test_get_chat_members(self):
        response    = self.client.get(self.url)
        membersList = json.loads(response.content)["membersList"]

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(membersList), 2)
        self.assertEqual(membersList[0]['uid'], self.uid1)
        self.assertEqual(membersList[1]['uid'], self.uid2)

    def test_add_chat_member(self):
        response = self.client.post(
            self.url,
            json.dumps({
                'uid': self.user3.uid,
            }),
            content_type='application/json'
        )

        chatMembers  = ChatMember.objects.filter(chat=self.chat)
        isChatMember = ChatMember.objects.filter(chat=self.chat, member=self.user3).exists()

        self.assertEqual(response.status_code, 201)
        self.assertEqual(len(chatMembers), 3)
        self.assertEqual(isChatMember, True)

    def test_remove_chat_member(self):
        response = self.client.delete(
            self.url,
            json.dumps({
                'uid': self.user2.uid,
            }),
            content_type='application/json'
        )

        chatMembers  = ChatMember.objects.filter(chat=self.chat)
        isChatMember = ChatMember.objects.filter(chat=self.chat, member=self.user2).exists()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(chatMembers), 1)
        self.assertEqual(isChatMember, False)

