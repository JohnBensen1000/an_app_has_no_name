import json
import sys

from django.test import TestCase, Client, client
from django.urls import reverse
from django.apps import apps
from django.core.files.uploadedfile import SimpleUploadedFile

User          = apps.get_model("models", "User")
Preferences   = apps.get_model("models", "Preferences")
Profile       = apps.get_model("models", "Profile")
Following     = apps.get_model("models", "Following")
ChatMember    = apps.get_model("models", "ChatMember")
Chat          = apps.get_model("models", "Chat")
WatchedBy     = apps.get_model("models", "WatchedBy")
Blocked       = apps.get_model("models", "Blocked")
Reported      = apps.get_model("models", "Reported")
Post          = apps.get_model("models", "Post")

class SignedInStatusTests(TestCase):
    def setUp(self):
        self.userID   = "John"
        self.username = "John Bensen"
        self.uid      = '12345'
    
        self.client = Client()
        self.url    = reverse('signedInStatus', kwargs={'uid': self.uid})

        self.user = User.objects.create(
            userID   = self.userID,
            email    = self.userID + "@gmail.com",
            phone    = self.userID + "12345",
            username = self.username,
            uid      = self.uid,
            preferences = Preferences.objects.create(),
            profile     = Profile.objects.create(),
        )

    def test_sign_in(self):
        deviceToken = "abc"
        response = self.client.post(
            self.url, 
            json.dumps({
                'signIn':      True,
                'deviceToken': deviceToken
            }), 
            content_type='application/json'
        )

        updatedUser = User.objects.get(uid=self.uid)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(updatedUser.signedIn, True)
        self.assertEqual(updatedUser.deviceToken, deviceToken)

    def test_sign_in_on_another_device(self):
        deviceToken1 = "abc"
        response = self.client.post(
            self.url, 
            json.dumps({
                'signIn':      True,
                'deviceToken': deviceToken1,
            }), 
            content_type='application/json'
        )

        deviceToken2 = "def"
        response = self.client.post(
            self.url, 
            json.dumps({
                'signIn':      True,
                'deviceToken': deviceToken2,
            }), 
            content_type='application/json'
        )

        updatedUser = User.objects.get(uid=self.uid)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(updatedUser.signedIn, True)
        self.assertEqual(updatedUser.deviceToken, deviceToken2)

class SignedInTest(TestCase):
    def setUp(self):
        self.userID   = "John"
        self.username = "John Bensen"
        self.uid      = '12345'
    
        self.client = Client()
        self.url    = reverse('deviceSignedInOn')

        self.user = User.objects.create(
            userID   = self.userID,
            email    = self.userID + "@gmail.com",
            phone    = self.userID + "12345",
            username = self.username,
            uid      = self.uid,
            preferences = Preferences.objects.create(),
            profile     = Profile.objects.create(),
        )    

    def test_signed_out(self):
        response = self.client.get(self.url + '?deviceToken=abcedf')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content)['signedIn'], False)

    def test_signed_in(self):
        self.user.signedIn    = True
        self.user.deviceToken = "abcedf"
        self.user.save()

        response     = self.client.get(self.url + '?deviceToken=abcedf')
        responseBody = json.loads(response.content)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(responseBody['signedIn'], True)
        self.assertEqual(responseBody['user']['uid'], self.uid)

class TestChats(TestCase):
    def setUp(self):
        self.client = Client()
        self.user1  = self._create_user_object("rob", "rob123")
        self.user2  = self._create_user_object("evan", "evan123")
        self.user3  = self._create_user_object("drew", "drew123")
        self.user4  = self._create_user_object("andrew", "andrew123")

        self.chat1 = self._create_direct_message_object("Chat1", "big banana", self.user1, self.user2)
        self.chat2 = self._create_direct_message_object("Chat2", "smaill banana", self.user1, self.user3)

    def _create_user_object(self, userID, username):
        return User.objects.create(
            userID      = userID,
            email       = userID + '@gmail.com',
            username    = username,
            preferences = Preferences.objects.create(),
            profile     = Profile.objects.create(),
            uid         = userID + username
        )

    def _create_direct_message_object(self, chatID, chatName, user1, user2):
        chat = Chat.objects.create(
            chatID          = chatID,
            chatName        = chatName,
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
            isOwner = False
        )

        return chat

    def test_get_list_of_chats(self):
        url1      = reverse('chats', kwargs={'uid': self.user1.uid})
        response1 = self.client.get(url1)
        chatList1 = json.loads(response1.content)['chats']

        url4      = reverse('chats', kwargs={'uid': self.user4.uid})
        response4 = self.client.get(url4)
        chatList4 = json.loads(response4.content)['chats']

        self.assertEqual(response1.status_code, 200)
        self.assertEqual(len(chatList1), 2)

        self.assertEqual(response4.status_code, 200)
        self.assertEqual(len(chatList4), 0)

    def test_post_chat_text(self):
        url      = reverse('chat', kwargs={'uid': self.user1.uid, 'chatID': self.chat1.chatID})
        response = self.client.post(
            url,
            json.dumps({
                'isPost': False,
                'text':   'Hello World!'
            }),
            content_type='application/json'
        )

        chatMember1 = ChatMember.objects.filter(chat__chatID=self.chat1.chatID).filter(member__uid=self.user1.uid).first()
        chatMember2 = ChatMember.objects.filter(chat__chatID=self.chat1.chatID).filter(member__uid=self.user2.uid).first()

        self.assertEqual(response.status_code, 201)
        self.assertTrue(chatMember1.isUpdated)
        self.assertFalse(chatMember2.isUpdated)

    def test_post_updated(self):
        chatMember1           = ChatMember.objects.filter(chat__chatID=self.chat1.chatID).filter(member__uid=self.user1.uid).first()
        chatMember2           = ChatMember.objects.filter(chat__chatID=self.chat2.chatID).filter(member__uid=self.user1.uid).first()
        chatMember1.isUpdated = False
        chatMember2.isUpdated = False
        chatMember1.save()
        chatMember2.save()

        url      = reverse('updated', kwargs={'uid': self.user1.uid, 'chatID': self.chat1.chatID})
        response = self.client.post(url)

        chatMember1 = ChatMember.objects.filter(chat__chatID=self.chat1.chatID).filter(member__uid=self.user1.uid).first()
        chatMember2 = ChatMember.objects.filter(chat__chatID=self.chat2.chatID).filter(member__uid=self.user1.uid).first()

        self.assertEqual(response.status_code, 200)
        self.assertTrue(chatMember1.isUpdated)
        self.assertFalse(chatMember2.isUpdated)

class TestNewContent(TestCase):
    def setUp(self):
        self.client = Client()
        self.user   = self.create_user_object("test", "test")
        self.users  = [
            self.create_user_object("test1", "test1"),
            self.create_user_object("test2", "test2"),
            self.create_user_object("test3", "test3"),
            self.create_user_object("test4", "test4"),
            self.create_user_object("test5", "test5"),
        ]
        Following.objects.create(
            follower    = self.user,
            creator     = self.users[0],
            newFollower = False
        )
        Following.objects.create(
            follower    = self.user,
            creator     = self.users[1],
            newFollower = False
        )
        Blocked.objects.create(
            user    = self.user,
            creator = self.users[4]
        )

    def create_user_object(self, userID, username):
        return User.objects.create(
            userID      = userID,
            email       = userID + '@gmail.com',
            username    = username,
            preferences = Preferences.objects.create(),
            profile     = Profile.objects.create(),
            uid         = userID + username
        )

    def create_post_object(self, postID, user, isPrivate):
        return Post.objects.create(
            postID      = postID,
            creator     = user,
            isImage     = True,
            isPrivate   = isPrivate, 
            downloadURL = "fakewebsite.com",
            preferences = Preferences.objects.create(),
        )

    def test_get_posts_from_followings(self):
        '''
            Creates some posts from users that the user follows, some posts from users
            that the user doesn't follow. Then checks to see if the posts returned are 
            only from creators that the user follows.
        '''
        postFollowing0 = self.create_post_object("0", self.users[0], False)
        postFollowing1 = self.create_post_object("1", self.users[1], False)
        postFollowing2 = self.create_post_object("2", self.users[1], False)
        postFollowing3 = self.create_post_object("3", self.users[0], False)

        self.create_post_object("4", self.users[3], False)
        self.create_post_object("5", self.users[2], False)

        url      = reverse('following_content', kwargs={'uid': self.user.uid})
        response = self.client.get(url)
        postList = json.loads(response.content)["posts"]
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(postList), 4)
        self.assertEqual(postList[0]["postID"], postFollowing3.postID)
        self.assertEqual(postList[1]["postID"], postFollowing2.postID)
        self.assertEqual(postList[2]["postID"], postFollowing1.postID)
        self.assertEqual(postList[3]["postID"], postFollowing0.postID)

    def test_get_posts_from_followers_not_watched(self):
        '''
            Creates some posts from users that the user follows, records that the user has
            already watched some of these posts. Posts that the user hasn't watched should
            appear first, then posts that the user hasn't watched should appear after. 
        '''

        postFollowing0 = self.create_post_object("0", self.users[0], False)
        postFollowing1 = self.create_post_object("1", self.users[1], False)
        postFollowing2 = self.create_post_object("2", self.users[1], False)
        postFollowing3 = self.create_post_object("3", self.users[0], False)
        postFollowing4 = self.create_post_object("4", self.users[0], False)

        WatchedBy.objects.create(user=self.user, post=postFollowing3)
        WatchedBy.objects.create(user=self.user, post=postFollowing4)

        url      = reverse('following_content', kwargs={'uid': self.user.uid})
        response = self.client.get(url)
        postList = json.loads(response.content)["posts"]

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(postList), 5)
        self.assertEqual(postList[0]["postID"], postFollowing2.postID)
        self.assertEqual(postList[1]["postID"], postFollowing1.postID)
        self.assertEqual(postList[2]["postID"], postFollowing0.postID)
        self.assertEqual(postList[3]["postID"], postFollowing4.postID)
        self.assertEqual(postList[4]["postID"], postFollowing3.postID)

    def test_get_recommendations_list(self):
        '''
            Tests the list of posts that the recommendation view returns. The return list of
            posts should not contain posts created by the user or created by creators that the
            user is following or has blocked. The list should start off with posts that the 
            user hasn't watched, and the rest of the list should be posts that the user already
            watched.
        '''
        self.create_post_object("10", self.user, False)

        self.create_post_object("0", self.users[0], False)
        self.create_post_object("1", self.users[1], False)
        self.create_post_object("2", self.users[1], False)

        self.create_post_object("8", self.users[4], False)
        self.create_post_object("9", self.users[4], False)

        postNotFollowing0 = self.create_post_object("3", self.users[2], False)
        postNotFollowing1 = self.create_post_object("4", self.users[3], False)
        postNotFollowing2 = self.create_post_object("5", self.users[2], False)
        postNotFollowing3 = self.create_post_object("6", self.users[2], False)
        postNotFollowing4 = self.create_post_object("7", self.users[3], False)

        WatchedBy.objects.create(user=self.user, post=postNotFollowing3)
        WatchedBy.objects.create(user=self.user, post=postNotFollowing2)

        url      = reverse('recommendations', kwargs={'uid': self.user.uid})
        response = self.client.get(url)
        postList = json.loads(response.content)["posts"]
        postIds  = [post["postID"] for post in postList]

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(postList), 5)

        self.assertTrue(postNotFollowing4.postID in postIds)
        self.assertTrue(postNotFollowing0.postID in postIds)
        self.assertTrue(postNotFollowing1.postID in postIds)

        self.assertEqual(postList[3]["postID"], postNotFollowing3.postID)
        self.assertEqual(postList[4]["postID"], postNotFollowing2.postID)

    def test_get_recommendations_list_excluding_reported_posts(self):
        '''
            This test exclusively checks if the reported posts are excluded from the list of
            recommendated posts. 
        '''
        postNotFollowing0 = self.create_post_object("0", self.users[2], False)
        postNotFollowing1 = self.create_post_object("1", self.users[3], False)
        postNotFollowing2 = self.create_post_object("2", self.users[2], False)

        postReported0 = self.create_post_object("3", self.users[3], False)
        postReported1 = self.create_post_object("4", self.users[2], False)

        Reported.objects.create(user=self.user, post=postReported0)
        Reported.objects.create(user=self.user, post=postReported1)

        url      = reverse('recommendations', kwargs={'uid': self.user.uid})
        response = self.client.get(url)
        postList = json.loads(response.content)["posts"]
        postIds  = [post["postID"] for post in postList]

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(postList), 3)

        self.assertTrue(postNotFollowing0.postID in postIds)
        self.assertTrue(postNotFollowing1.postID in postIds)
        self.assertTrue(postNotFollowing2.postID in postIds)

        self.assertFalse(postReported0.postID in postIds)
        self.assertFalse(postReported1.postID in postIds)

class PostsTests(TestCase):
    def setUp(self):
        self.userID   = "John"
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

        self.client = Client()
        self.url    = reverse('posts', kwargs={'uid': self.uid})

    def test_upload_post(self):
        downloadURL = "downloadURL"

        response = self.client.post(
            self.url, json.dumps({
                'isPost':   True,
                'isImage':  True,
                'isPrivate': True,
                'downloadURL': downloadURL
            }),
            content_type='application/json'
        )

        post = Post.objects.first()

        self.assertEqual(response.status_code, 201)
        self.assertEqual(post.creator.uid, self.uid)
        self.assertEqual(post.isImage, True)
        self.assertEqual(post.isPrivate, True)     

    def test_get_posts(self):
        post1 = Post.objects.create(
            postID      = '1234',
            isPrivate   = True,
            isImage     = False,
            downloadURL = "5454",
            preferences = Preferences.objects.create(),
            creator     = self.user
        )
        post2 = Post.objects.create(
            postID      = '121234',
            isPrivate   = False,
            isImage     = False,
            downloadURL = "544554",
            preferences = Preferences.objects.create(),
            creator     = self.user
        )
        post3 = Post.objects.create(
            postID      = '124334',
            isPrivate   = True,
            isImage     = True,
            downloadURL = "54243554",
            preferences = Preferences.objects.create(),
            creator     = self.user
        )

        response     = self.client.get(self.url)
        responseBody = json.loads(response.content)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(responseBody['posts']), 3)
        for postJson in responseBody['posts']:
            self.assertEqual(postJson["creator"]["uid"], self.uid)

class ProfileTest(TestCase):
    def setUp(self):
        self.userID   = "John"
        self.username = "John Bensen"
        self.uid      = 'UNIT_TEST'
        self.postID   = "1"

        self.user = User.objects.create(
            userID   = self.userID,
            email    = self.userID + "@gmail.com",
            phone    = self.userID + "12345",
            username = self.username,
            uid      = self.uid,
            preferences = Preferences.objects.create(),
            profile     = Profile.objects.create(),
        )

        self.client = Client()
        self.url    = reverse('profile', kwargs={'uid': self.uid})

    def test_get_profile(self):
        downloadURL = 'testURL'

        self.user.profile.exists      = True
        self.user.profile.isImage     = True
        self.user.profile.downloadURL = downloadURL
        self.user.profile.save()

        response     = self.client.get(self.url)
        responseBody = json.loads(response.content)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(responseBody['exists'], True)
        self.assertEqual(responseBody['isImage'], True)
        self.assertEqual(responseBody['downloadURL'], downloadURL)

    def test_post_profile(self):
        downloadURL = "downloadURL"

        response = self.client.post(
            self.url, json.dumps({
                'isImage':  True,
                'downloadURL': downloadURL
            }),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 201)

class PostTest(TestCase):
    def setUp(self):
        self.userID   = "John"
        self.username = "John Bensen"
        self.uid      = 'UNIT_TEST'
        self.postID   = "1"

        self.user = User.objects.create(
            userID   = self.userID,
            email    = self.userID + "@gmail.com",
            phone    = self.userID + "12345",
            username = self.username,
            uid      = self.uid,
            preferences = Preferences.objects.create(),
            profile     = Profile.objects.create(),
        )

        self.post = Post.objects.create(
            postID      = self.postID,
			preferences = Preferences.objects.create(),
            creator     = self.user,
            isImage	    = True,
            isPrivate   = False,
            downloadURL = "123.com"
        )
        self.client = Client()
        self.url    = reverse('post', kwargs={'uid': self.uid, 'postID': self.postID})

    def test_set_private(self):
        response = self.client.post(
            self.url, 
            json.dumps({
                "isPrivate": True
            }),
            content_type='application/json'
        )

        updatedPost = Post.objects.get(postID=self.postID)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(updatedPost.isPrivate, True)

    def test_delete_post(self):
        response = self.client.delete(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Preferences.objects.count(), 1)
        self.assertEqual(Post.objects.count(), 0)

    def test_not_authorized(self):
        url = reverse('post', kwargs={'uid': 'notCorrectUID', 'postID': self.postID})

        response = self.client.delete(url)

        self.assertEqual(response.status_code, 401)
    
class WatchedListTests(TestCase):
    def setUp(self):
        self.userID   = "John"
        self.username = "John Bensen"
        self.uid      = 'UNIT_TEST'
        self.postID   = "1"

        self.user = User.objects.create(
            userID   = self.userID,
            email    = self.userID + "@gmail.com",
            phone    = self.userID + "12345",
            username = self.username,
            uid      = self.uid,
            preferences = Preferences.objects.create(),
            profile     = Profile.objects.create(),
        )

        self.post = Post.objects.create(
            postID      = self.postID,
			preferences = Preferences.objects.create(),
            creator     = self.user,
            isImage	    = True,
            isPrivate   = False,
            downloadURL = "123.com"
        )
        self.client = Client()
        self.url    = reverse('watched_list', kwargs={'postID': self.postID})
        
    def test_record_watched(self):
        userID   = "Andrew"
        username = "andrew"
        uid      = "123"

        user = User.objects.create(     
            userID   = userID,
            email    = userID + "@gmail.com",
            phone    = userID + "12345",
            username = username,
            uid      = uid,
            preferences = Preferences.objects.create(),
            profile     = Profile.objects.create(),
        )

        response = self.client.post(
            self.url,
            json.dumps({
                "uid": uid,
                "userRating": 1,
            }),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(WatchedBy.objects.count(), 1)
        self.assertEqual(WatchedBy.objects.first().user.uid, uid)

class ReportsTest(TestCase):
    def setUp(self):
        self.userID   = "John"
        self.username = "John Bensen"
        self.uid      = 'UNIT_TEST'
        self.postID   = "1"

        self.user = User.objects.create(
            userID   = self.userID,
            email    = self.userID + "@gmail.com",
            phone    = self.userID + "12345",
            username = self.username,
            uid      = self.uid,
            preferences = Preferences.objects.create(),
            profile     = Profile.objects.create(),
        )

        self.post = Post.objects.create(
            postID      = self.postID,
            preferences = Preferences.objects.create(),
            creator     = self.user,
            isImage	    = True,
            isPrivate   = False,
            downloadURL = "123.com"
        )
        self.client = Client()
        self.url    = reverse('reports', kwargs={'uid': self.uid}) 

    def test_post_report(self):
        response = self.client.post(
            self.url,
            json.dumps({
                "postID": self.postID,
            }),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Reported.objects.filter(user=self.user, post=self.post).exists(), True)

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
        Following.objects.create(
            follower    = self.user,
            creator     = self.user1,
            newFollower = True, 
        )
        Following.objects.create(
            follower    = self.user,
            creator     = self.user2,
            newFollower = True, 
        )
        Following.objects.create(
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
        Following.objects.create(
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

        relation1 = Following.objects.get(follower=self.user, creator=self.user1)
        relation2 = Following.objects.get(follower=self.user, creator=self.user2)

        self.assertEqual(ChatMember.objects.filter(member=self.user)[0].chat, ChatMember.objects.filter(member=self.user2)[0].chat)

        self.assertEqual(response1.status_code, 201)
        self.assertEqual(response2.status_code, 201)

        self.assertEqual(relation1.newFollower, True)
        self.assertEqual(relation2.newFollower, False)

    def test_start_following_blocked_creator(self):
        Blocked.objects.create(
            user    = self.user,
            creator = self.user1
        )

        response = self.client.post(
            self.url, 
            json.dumps({
                'uid': self.user1.uid
            }),
            content_type='application/json'
        )

        doesUserBlockCreator = Blocked.objects.filter(user=self.user, creator=self.user1).exists()

        self.assertEqual(response.status_code, 201)
        self.assertEqual(doesUserBlockCreator, False)


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

        Following.objects.create(
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

        following          = Following.objects.get(follower=self.user1, creator=self.user2)
        newFollowingExists = Following.objects.filter(follower=self.user2, creator=self.user1).exists()

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

        following = Following.objects.get(follower=self.user1, creator=self.user2)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(following.newFollower, False)

    def test_delete_friendship(self):
        Following.objects.create(
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

        Following.objects.create(
            follower    = self.user2,
            creator     = self.user1,
            newFollower = True, 
        )
        Following.objects.create(
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

        Following.objects.create(
            follower    = self.user2,
            creator     = self.user1,
            newFollower = True, 
        )
        Following.objects.create(
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

        Following.objects.create(
            follower    = self.user2,
            creator     = self.user1,
            newFollower = True, 
        )
        Following.objects.create(
            follower    = self.user3,
            creator     = self.user1,
            newFollower = False, 
        )
        Following.objects.create(
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

class BlockedTest(TestCase):
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
            userID   = 'laura',
            email    = "jake1211@gmail.com",
            phone    = "123212334245",
            username = 'jakelessman',
            uid      = '101010101',
            preferences = Preferences.objects.create(),
            profile     = Profile.objects.create(),
        )
        self.user4 = User.objects.create(
            userID   = 'collin',
            email    = "jake112211@gmail.com",
            phone    = "12312212334245",
            username = 'jakelessman',
            uid      = '12121321231',
            preferences = Preferences.objects.create(),
            profile     = Profile.objects.create(),
        )

        self.client = Client()
        self.url   = reverse('blocked', kwargs={'uid': self.user1.uid})

    def test_block_user(self):
        response = self.client.post(
            self.url,
            json.dumps({
                'uid': self.user2.uid
            }),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Blocked.objects.filter(user=self.user1, creator=self.user2).exists(), True)

    def test_get_blocked_creators(self):
        Blocked.objects.create(user=self.user1, creator=self.user2)
        Blocked.objects.create(user=self.user1, creator=self.user4)

        response         = self.client.get(self.url)
        blockedUsersUids = [user["uid"] for user in json.loads(response.content)['blocked']]

        self.assertEqual(response.status_code, 200)
        self.assertTrue(self.user2.uid in blockedUsersUids)
        self.assertTrue(self.user4.uid in blockedUsersUids)
        self.assertFalse(self.user3.uid in blockedUsersUids)

    def test_unblock_user(self):
        Blocked.objects.create(
            user    = self.user1,
            creator = self.user2,
        )

        url = reverse("blocked_user", kwargs={"uid": self.user1.uid, "creator_uid": self.user2.uid})

        response = self.client.delete(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Blocked.objects.filter(user=self.user1, creator=self.user2).exists(), False)

    def test_blocking_creator_that_user_follows(self):
        Following.objects.create(
            follower = self.user1,
            creator  = self.user2
        )

        response = self.client.post(
            self.url,
            json.dumps({
                'uid': self.user2.uid
            }),
            content_type='application/json'
        )

        doesUserBlockCreator  = Blocked.objects.filter(user=self.user1, creator=self.user2).exists()
        doesUserFollowCreator = Following.objects.filter(follower=self.user1, creator=self.user2).exists()

        self.assertEqual(response.status_code, 201)
        self.assertEqual(doesUserBlockCreator, True)
        self.assertEqual(doesUserFollowCreator, False)

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