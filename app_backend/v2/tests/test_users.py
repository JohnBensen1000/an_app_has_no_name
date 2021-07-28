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

class UserTests(BaseTest):
    def setUp(self):
        self.client = Client()

    def test_create_account(self):
        '''
            Creates a new account and tests to see if there is a new account and that the
            new account has all the correct information.
        '''
        response = self.client.post(
            reverse('users'),
            json.dumps({
                'userID': 'Laura1000',
                'email': 'email@gmail.com',
                'uid': 'laura1313',
                'username': 'Laura Hayes',
            }), 
            content_type='application/json'
        )

        user = User.objects.first()
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(user.userID, 'Laura1000')
        self.assertEqual(user.email,  'email@gmail.com')
        self.assertEqual(user.uid, 'laura1313')
        self.assertEqual(user.username, 'Laura Hayes')

    def test_create_account_when_user_id_taken(self):
        '''
            If someone tries to create a new account with a userID that is already taken,
            then a new account should not be created. This test ensures that now new account
            is created in this scenario. 
        '''
        self.create_user_object('user1', 'user1')

        response    = self.client.post(
            reverse('users'),
            json.dumps({
                'userID': 'user1',
                'email': 'email@gmail.com',
                'uid': 'laura1313',
                'username': 'Laura Hayes',
            }), 
            content_type='application/json'
        )
        responseBody = json.loads(response.content)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(responseBody['denied'], 'userIdTaken')
        self.assertEqual(User.objects.count(), 1)
        
    def test_search_strings(self):  
        '''
            Tests to see if the search view works. When given a string, this view should return
            a list of all users whose userId contains the given string. This test creates 4 users
            and searchs for different strings. 
        ''' 
        self.create_user_object('john1000', 'john')
        self.create_user_object('laura1000', 'laura')
        self.create_user_object('andrew1000', 'andrew')
        self.create_user_object('kishan1010', 'kishan')

        url = reverse('users')

        responseBody1 = json.loads(self.client.get(url, {'contains': 'john'}    ).content)
        responseBody2 = json.loads(self.client.get(url, {'contains': 'laura1'}  ).content)
        responseBody3 = json.loads(self.client.get(url, {'contains': 'a'}       ).content)
        responseBody4 = json.loads(self.client.get(url, {'contains': '10'}      ).content)
        responseBody5 = json.loads(self.client.get(url, {'contains': 'n10'}     ).content)
        responseBody6 = json.loads(self.client.get(url, {'contains': 'zoa'}     ).content)
        responseBody7 = json.loads(self.client.get(url, {'contains': ''}        ).content)
        responseBody8 = json.loads(self.client.get(url, {'contains': 'john1000'}).content)

        self.assertEquals(len(responseBody1['creatorsList']), 1)
        self.assertEquals(len(responseBody2['creatorsList']), 1)
        self.assertEquals(len(responseBody3['creatorsList']), 3)
        self.assertEquals(len(responseBody4['creatorsList']), 4)
        self.assertEquals(len(responseBody5['creatorsList']), 2)
        self.assertEquals(len(responseBody6['creatorsList']), 0)
        self.assertEquals(len(responseBody7['creatorsList']), 0)
        self.assertEquals(len(responseBody8['creatorsList']), 1)

    def test_search_strings_with_blocked_creators(self):
        '''
            The search view should not return blocked users. This test creates some "blocked" fields
            between the user and other users. These other users should not appear in the returned
            list of users. 
        '''
        user1 = self.create_user_object('john1000', 'john')
        user2 = self.create_user_object('laura1000', 'laura')
        self.create_user_object('andrew1010', 'andrew')
        self.create_user_object('kishan1010', 'kishan')

        user = self.create_user_object('test', 'test')

        Blocked.objects.create(user=user, creator=user1)
        Blocked.objects.create(user=user, creator=user2)

        url = reverse('users')

        responseBody1 = json.loads(
            self.client.get(url, {'contains': '1000', 'uid': user.uid}).content)
        responseBody2 = json.loads(
            self.client.get(url, {'contains': '10', 'uid': user.uid}).content)
        responseBody3 = json.loads(
            self.client.get(url, {'contains': 'a', 'uid': user.uid}).content)
        responseBody4 = json.loads(
            self.client.get(url, {'contains': 'kishan1010', 'uid': user.uid}).content)
        responseBody5 = json.loads(
            self.client.get(url, {'contains': 'john1000', 'uid': user.uid}).content)

        self.assertEqual(len(responseBody1['creatorsList']), 0)
        self.assertEqual(len(responseBody2['creatorsList']), 2)
        self.assertEqual(len(responseBody3['creatorsList']), 2)
        self.assertEqual(len(responseBody4['creatorsList']), 1)
        self.assertEqual(len(responseBody5['creatorsList']), 0)

    def test_get_user_by_uid(self):
        '''
            Searchs for an individual user, should get the user's dict as a json object.
        '''

        user         = self.create_user_object('test', 'test')
        url          = reverse('user', kwargs={'uid': user.uid})
        responseBody = json.loads(self.client.get(url).content)

        self.assertEqual(responseBody['userID'],   user.userID)
        self.assertEqual(responseBody['uid'],      user.uid)
        self.assertEqual(responseBody['username'], user.username)

    def update_user_data(self):
        '''
            Sends updated data to a user's account and tests to see if their account data has
            been updated correctly.
        '''

        user = self.create_user_object('test', 'test')

        url      = reverse('user', kwargs={'uid': user.uid})
        response = self.client.put(
            url, 
            json.dumps({
                'profileColor': '2',
                'username': 'username'
            }), 
            content_type='application/json'
        )

        user = User.objects.get(uid=user.uid)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(user.profileColor, '2')
        self.assertEqual(user.username, 'username')

    def test_delete_account(self):
        '''
            When a user deletes their account, makes sure that all the direct messages they are
            in are also deleted.
        '''
        user1 = self.create_user_object("test1", "test1")
        user2 = self.create_user_object("test2", "test2")
        chat  = Chat.objects.create(
            chatID          = "chatID",
            chatName        = "chatName",
            isDirectMessage = True
        )
        ChatMember.objects.create(
            member  = user1,
            chat    = chat,
            isOwner = True
        )
        ChatMember.objects.create(
            member  = user2,
            chat    = chat,
            isOwner = True
        )

        url      = reverse("user", kwargs={'uid': user1.uid})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(Chat.objects.count(), 0)
        self.assertEqual(ChatMember.objects.count(), 0)
        self.assertEqual(ChatMember.objects.filter(member=user2).count(), 0)

    # def test_get_user_preferences(self):
    #     '''
    #         Gets the list of the user's preferences.
    #     '''
    #     user         = self.create_user_object('test', 'test')
    #     url          = reverse('user_preferences', kwargs={'uid': user.uid})
    #     response     = self.client.get(url)

    #     self.assertEqual(response.status_code, 200)

    # def test_update_user_preferences(self):
    #     '''
    #         Gets the list of the user's preferences.
    #     '''
    #     user     = self.create_user_object('test', 'test')
    #     url      = reverse('user_preferences', kwargs={'uid': user.uid})
    #     response = self.client.put(
    #         url,
    #         json.dumps({
    #             'preferences': ['music', 'fitness', 'art']
    #         }),
    #         content_type='application/json'
    #     )

    #     user = User.objects.get(uid=user.uid)

    #     self.assertEqual(response.status_code, 200)
    #     self.assertEqual(user.preferences.music, .9)
    #     self.assertEqual(user.preferences.fitness, .9)
    #     self.assertEqual(user.preferences.art, .9)
    #     self.assertEqual(user.preferences.food, .1)
    #     self.assertEqual(user.preferences.comedy, .1)
    #     self.assertEqual(user.preferences.dance, .1)


