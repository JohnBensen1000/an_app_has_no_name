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

        url      = reverse('following', kwargs={'uid': self.user.uid})
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

        url      = reverse('following', kwargs={'uid': self.user.uid})
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