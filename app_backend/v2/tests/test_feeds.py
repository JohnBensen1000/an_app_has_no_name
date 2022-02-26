import json
import time 

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
WatchedBy     = apps.get_model("models", "WatchedBy")
Reported      = apps.get_model("models", "Reported")

class TestFeeds(BaseTest):
    def setUp(self):
        self.user   = self.create_user_object('test', 'test')
        self.cleint = Client()

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

    def test_get_posts_from_followings(self):
        '''
            Creates some posts from users that the user follows, some posts from users
            that the user doesn't follow. Then checks to see if the posts returned are 
            only from creators that the user follows.
        '''
        postFollowing0 = self.create_post_object(self.users[0], postID='1')
        postFollowing1 = self.create_post_object(self.users[1], postID='2')
        postFollowing2 = self.create_post_object(self.users[1], postID='3')
        postFollowing3 = self.create_post_object(self.users[0], postID='4')

        postFollowing4 = self.create_post_object(self.users[3], postID='5')
        postFollowing5 = self.create_post_object(self.users[2], postID='6')

        url      = reverse('following_feed')
        response = self.client.get(url, {'uid': self.user.uid})
        postList = json.loads(response.content)["posts"]
        postIds  = [post["postID"] for post in postList]
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(postList), 4)

        self.assertEqual(postIds[0], postFollowing3.postID)
        self.assertEqual(postIds[1], postFollowing2.postID)
        self.assertEqual(postIds[2], postFollowing1.postID)
        self.assertEqual(postIds[3], postFollowing0.postID)

        self.assertFalse(postFollowing4.postID in postIds)
        self.assertFalse(postFollowing5.postID in postIds)

    def test_get_posts_from_followings_not_watched(self):
        '''
            Creates some posts from users that the user follows, records that the user has
            already watched some of these posts. Posts that the user hasn't watched should
            appear first, then posts that the user hasn't watched should appear after. 
        '''

        postFollowing0 = self.create_post_object(self.users[0], postID='1')
        postFollowing1 = self.create_post_object(self.users[1], postID='2')
        postFollowing2 = self.create_post_object(self.users[1], postID='3')
        postFollowing3 = self.create_post_object(self.users[0], postID='4')
        postFollowing4 = self.create_post_object(self.users[0], postID='5')

        WatchedBy.objects.create(user=self.user, post=postFollowing3)
        WatchedBy.objects.create(user=self.user, post=postFollowing4)

        url      = reverse('following_feed')
        response = self.client.get(url, {'uid': self.user.uid})
        postList = json.loads(response.content)["posts"]
        postIds  = [post["postID"] for post in postList]

        notWatchedPostIds = postIds[:3]
        watchedPostIds    = postIds[3:]

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(postList), 5)

        self.assertTrue(postFollowing2.postID in notWatchedPostIds)
        self.assertTrue(postFollowing1.postID in notWatchedPostIds)
        self.assertTrue(postFollowing0.postID in notWatchedPostIds)
        self.assertTrue(postFollowing3.postID in watchedPostIds)
        self.assertTrue(postFollowing4.postID in watchedPostIds)

    def test_get_correct_number_of_following_posts(self):
        '''
            Checks to see if the following feed endpoint returns the correct number of posts.
        '''
        for i in range(45):
            self.create_post_object(self.users[i % 2], postID=str(i))

        url      = reverse('following_feed')
        response = self.client.get(url, {'uid': self.user.uid})
        postList = json.loads(response.content)["posts"]

        self.assertEqual(len(postList), 32)

    def test_get_correct_number_of_recommendations_posts(self):
        '''
            Checks to see if the recommendations feed endpoint returns the correct number of posts.
        '''
        for i in range(45):
            self.create_post_object(self.users[2], postID=str(i))

        url      = reverse('recommendations_feed')
        response = self.client.get(url, {'uid': self.user.uid})
        postList = json.loads(response.content)["posts"]

        self.assertEqual(len(postList), 32)

    def test_get_recommendations_list(self):
        '''
            Tests the list of posts that the recommendation view returns. The return list of
            posts should not contain posts created by the user or created by creators that the
            user is following or has blocked. The list should start off with posts that the 
            user hasn't watched, and the rest of the list should be posts that the user already
            watched.
        '''
        self.create_post_object(self.user)

        self.create_post_object(self.users[0], postID='1')
        self.create_post_object(self.users[1], postID='2')
        self.create_post_object(self.users[1], postID='3')

        self.create_post_object(self.users[4], postID='4')
        self.create_post_object(self.users[4], postID='5')

        postNotFollowing0 = self.create_post_object(self.users[2], postID='6')
        postNotFollowing1 = self.create_post_object(self.users[3], postID='7')
        postNotFollowing2 = self.create_post_object(self.users[2], postID='8')
        postNotFollowing3 = self.create_post_object(self.users[2], postID='9')
        postNotFollowing4 = self.create_post_object(self.users[3], postID='10')

        WatchedBy.objects.create(user=self.user, post=postNotFollowing3)
        WatchedBy.objects.create(user=self.user, post=postNotFollowing2)

        url      = reverse('recommendations_feed')
        response = self.client.get(url, {'uid': self.user.uid})
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
        postNotFollowing0 = self.create_post_object(self.users[2], postID='1')
        postNotFollowing1 = self.create_post_object(self.users[3], postID='2')
        postNotFollowing2 = self.create_post_object(self.users[2], postID='3')

        postReported0 = self.create_post_object(self.users[3], postID='4')
        postReported1 = self.create_post_object(self.users[2], postID='5')

        Reported.objects.create(user=self.user, post=postReported0)
        Reported.objects.create(user=self.user, post=postReported1)

        url      = reverse('recommendations_feed')
        response = self.client.get(url, {'uid': self.user.uid})
        postList = json.loads(response.content)["posts"]
        postIds  = [post["postID"] for post in postList]

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(postList), 3)

        self.assertTrue(postNotFollowing0.postID in postIds)
        self.assertTrue(postNotFollowing1.postID in postIds)
        self.assertTrue(postNotFollowing2.postID in postIds)

        self.assertFalse(postReported0.postID in postIds)
        self.assertFalse(postReported1.postID in postIds)

# class TestLoadTests(BaseTest):
#     '''
#         The point of these test cases is to load test the endpoints. Each test iteratively creates
#         different number of entries in the database, and then times how long the endpoint takes to
#         respond to each of the created scenarios.
#     '''
#     def setUp(self):
#         self.user   = self.create_user_object('test', 'test')
#         self.cleint = Client()

#         self.users  = [
#             self.create_user_object("test1", "test1"),
#             self.create_user_object("test2", "test2"),
#             self.create_user_object("test3", "test3"),
#             self.create_user_object("test4", "test4"),
#             self.create_user_object("test5", "test5"),
#             self.create_user_object("test6", "test6"),
#             self.create_user_object("test7", "test7"),
#             self.create_user_object("test8", "test8"),
#             self.create_user_object("test9", "test9"),
#             self.create_user_object("test10", "test10"),
#         ]

#     def set_up_followings(self):
#         for user in self.users:
#             Following.objects.create(
#                 follower    = self.user,
#                 creator     = user,
#                 newFollower = False
#             )

#     def set_up_posts(self, num_posts):
#         for user in self.users:
#             for i in range(num_posts // len(self.users)):
#                 self.create_post_object(user, user.uid + "_" + str(i))

#     def set_up_watched(self, num_watched):
#         for i in range(num_watched):
#             WatchedBy.objects.create(
#                 user = self.user,
#                 post = Post.objects.all()[i]
#             )

#     def get_time_to_return_posts(self, endpoint_name):
#         startTime = time.time()

#         url      = reverse(endpoint_name)
#         response = self.client.get(url, {'uid': self.user.uid})
#         json.loads(response.content)["posts"]

#         return time.time() - startTime

#     def test_following_load_num_posts(self):
#         '''
#             Tests the following feed endpoint as the number of posts increases. 
#         '''
#         self.set_up_followings()

#         num_posts_list = [10, 50, 100, 500, 1000, 5000, 10000]
#         results_list   = []

#         for num_posts in num_posts_list:
#             self.set_up_posts(num_posts)
#             time = self.get_time_to_return_posts("following_feed")
#             Post.objects.all().delete()
            
#             results_list.append(time)
#             # print("Time to load " + str(num_posts) + " posts: " + str(time))

#         # plt.plot(num_posts_list, results_list)
#         # plt.savefig("v2/tests/figures/plot3.png")
#         # plt.xlabel("Number of posts")
#         # plt.ylabel("Time to load (sec)")        

#     def test_following_load_num_watched_by(self):
#         '''
#             Tests the following feed endpoint as the number of watched-by entries increases.
#         '''
#         self.set_up_followings()

#         num_posts = 50000
#         self.set_up_posts(num_posts)

#         num_watched  = [10, 20, 50, 100, 200, 500, 1000, 2000, 5000, 10000, 20000]
#         results_list = []

#         for num_watched_posts in num_watched:
#             self.set_up_watched(num_watched_posts)
#             time = self.get_time_to_return_posts("following_feed")
#             WatchedBy.objects.all().delete()

#             results_list.append(time)
#             # print("Time to load " + str(num_watched_posts) + " watched posts: " + str(time))

#         # plt.plot(num_watched, results_list)
#         # plt.savefig("v2/tests/figures/plot3.png")
#         # plt.xlabel("Number of posts")
#         # plt.ylabel("Time to load (sec)")   

#     def test_recommendations_load(self):
#         '''
#             Tests the recommendation feed endpoint as the number of post entries and watched-by 
#             entries increases.
#         '''
#         num_posts_list   = [100, 200, 500, 1000, 2000, 5000, 10000, 20000, 50000]
#         num_watched_list = [ 50, 100, 200,  500, 1000, 2000,  5000, 10000, 20000]
#         results          = []

#         for num_posts, num_watched in zip(num_posts_list, num_watched_list):
#             self.set_up_posts(num_posts)
#             self.set_up_watched(num_watched)

#             time = self.get_time_to_return_posts("recommendations_feed")
#             results.append(time)
#             # print("Time to load with " + str(num_posts) + " posts and " + str(num_watched) + " watched posts: " + str(time))

#             Post.objects.all().delete()
#             WatchedBy.objects.all().delete()
        
#         # plt.plot(results)
#         # plt.savefig("v2/tests/figures/plot3.png")
#         # plt.xlabel("test_num")
#         # plt.ylabel("Time to load (sec)")

