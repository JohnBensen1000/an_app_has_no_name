import json
import sys

from django.test import TestCase, Client, client
from django.urls import reverse
from django.apps import apps
from django.core.files.uploadedfile import SimpleUploadedFile

User        = apps.get_model("models", "User")
Preferences = apps.get_model("models", "Preferences")
Profile     = apps.get_model("models", "Profile")
Post        = apps.get_model("models", "Post")

# class PostsTests(TestCase):
#     def setUp(self):
#         self.userID   = "John"
#         self.username = "John Bensen"
#         self.uid      = 'UNIT_TEST'

#         self.user = User.objects.create(
#             userID   = self.userID,
#             email    = self.userID + "@gmail.com",
#             phone    = self.userID + "12345",
#             username = self.username,
#             uid      = self.uid,
#             preferences = Preferences.objects.create(),
#             profile     = Profile.objects.create(),
#         )

#         self.client = Client()
#         self.url    = reverse('posts', kwargs={'uid': self.uid})

#     def test_upload_post(self):
#         downloadURL = "downloadURL"

#         response = self.client.post(
#             self.url, json.dumps({
#                 'isPost':   True,
#                 'isImage':  True,
#                 'isPrivate': True,
#                 'downloadURL': downloadURL
#             }),
#             content_type='application/json'
#         )

#         post = Post.objects.first()

#         self.assertEqual(response.status_code, 201)
#         self.assertEqual(post.creator.uid, self.uid)
#         self.assertEqual(post.isImage, True)
#         self.assertEqual(post.isPrivate, True)     

#     def test_get_posts(self):
#         post1 = Post.objects.create(
#             postID      = '1234',
#             isPrivate   = True,
#             isImage     = False,
#             downloadURL = "5454",
#             preferences = Preferences.objects.create(),
#             creator     = self.user
#         )
#         post2 = Post.objects.create(
#             postID      = '121234',
#             isPrivate   = False,
#             isImage     = False,
#             downloadURL = "544554",
#             preferences = Preferences.objects.create(),
#             creator     = self.user
#         )
#         post3 = Post.objects.create(
#             postID      = '124334',
#             isPrivate   = True,
#             isImage     = True,
#             downloadURL = "54243554",
#             preferences = Preferences.objects.create(),
#             creator     = self.user
#         )

#         response     = self.client.get(self.url)
#         responseBody = json.loads(response.content)

#         self.assertEqual(response.status_code, 200)
#         self.assertEqual(len(responseBody['posts']), 3)
#         for postJson in responseBody['posts']:
#             self.assertEqual(postJson["creator"]["uid"], self.uid)

# class ProfileTest(TestCase):
#     def setUp(self):
#         self.userID   = "John"
#         self.username = "John Bensen"
#         self.uid      = 'UNIT_TEST'
#         self.postID   = "1"

#         self.user = User.objects.create(
#             userID   = self.userID,
#             email    = self.userID + "@gmail.com",
#             phone    = self.userID + "12345",
#             username = self.username,
#             uid      = self.uid,
#             preferences = Preferences.objects.create(),
#             profile     = Profile.objects.create(),
#         )

#         self.client = Client()
#         self.url    = reverse('profile', kwargs={'uid': self.uid})

#     def test_get_profile(self):
#         downloadURL = 'testURL'

#         self.user.profile.exists      = True
#         self.user.profile.isImage     = True
#         self.user.profile.downloadURL = downloadURL
#         self.user.profile.save()

#         response     = self.client.get(self.url)
#         responseBody = json.loads(response.content)

#         self.assertEqual(response.status_code, 200)
#         self.assertEqual(responseBody['exists'], True)
#         self.assertEqual(responseBody['isImage'], True)
#         self.assertEqual(responseBody['downloadURL'], downloadURL)

#     def test_post_profile(self):
#         downloadURL = "downloadURL"

#         response = self.client.post(
#             self.url, json.dumps({
#                 'isImage':  True,
#                 'downloadURL': downloadURL
#             }),
#             content_type='application/json'
#         )

#         self.assertEqual(response.status_code, 201)

# class PostTest(TestCase):
#     def setUp(self):
#         self.userID   = "John"
#         self.username = "John Bensen"
#         self.uid      = 'UNIT_TEST'
#         self.postID   = "1"

#         self.user = User.objects.create(
#             userID   = self.userID,
#             email    = self.userID + "@gmail.com",
#             phone    = self.userID + "12345",
#             username = self.username,
#             uid      = self.uid,
#             preferences = Preferences.objects.create(),
#             profile     = Profile.objects.create(),
#         )

#         self.post = Post.objects.create(
#             postID      = self.postID,
# 			preferences = Preferences.objects.create(),
#             creator     = self.user,
#             isImage	    = True,
#             isPrivate   = False,
#             downloadURL = "123.com"
#         )
#         self.client = Client()
#         self.url    = reverse('post', kwargs={'uid': self.uid, 'postID': self.postID})

#     def test_set_private(self):
#         response = self.client.post(
#             self.url, 
#             json.dumps({
#                 "isPrivate": True
#             }),
#             content_type='application/json'
#         )

#         updatedPost = Post.objects.get(postID=self.postID)

#         self.assertEqual(response.status_code, 200)
#         self.assertEqual(updatedPost.isPrivate, True)

#     def test_delete_post(self):
#         response = self.client.delete(self.url)

#         self.assertEqual(response.status_code, 200)
#         self.assertEqual(Preferences.objects.count(), 1)
#         self.assertEqual(Post.objects.count(), 0)

#     def test_not_authorized(self):
#         url = reverse('post', kwargs={'uid': 'notCorrectUID', 'postID': self.postID})

#         response = self.client.delete(url)

#         self.assertEqual(response.status_code, 401)
    
# class WatchedListTests(TestCase):
#     def setUp(self):
#         self.userID   = "John"
#         self.username = "John Bensen"
#         self.uid      = 'UNIT_TEST'
#         self.postID   = "1"

#         self.user = User.objects.create(
#             userID   = self.userID,
#             email    = self.userID + "@gmail.com",
#             phone    = self.userID + "12345",
#             username = self.username,
#             uid      = self.uid,
#             preferences = Preferences.objects.create(),
#             profile     = Profile.objects.create(),
#         )

#         self.post = Post.objects.create(
#             postID      = self.postID,
# 			preferences = Preferences.objects.create(),
#             creator     = self.user,
#             isImage	    = True,
#             isPrivate   = False,
#             downloadURL = "123.com"
#         )
#         self.client = Client()
#         self.url    = reverse('watched_list', kwargs={'postID': self.postID})
        
#     def test_record_watched(self):
#         userID   = "Andrew"
#         username = "andrew"
#         uid      = "123"

#         user = User.objects.create(     
#             userID   = userID,
#             email    = userID + "@gmail.com",
#             phone    = userID + "12345",
#             username = username,
#             uid      = uid,
#             preferences = Preferences.objects.create(),
#             profile     = Profile.objects.create(),
#         )

#         response = self.client.post(
#             self.url,
#             json.dumps({
#                 "uid": uid,
#                 "userRating": 1,
#             }),
#             content_type='application/json'
#         )

#         self.assertEqual(response.status_code, 201)
#         self.assertEqual(self.post.watchedBy.count(), 1)
#         self.assertEqual(self.post.watchedBy.first().uid, uid)


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
        self.url    = reverse('reports', kwargs={'uid': self.uid, 'postID': self.postID}) 

    def test_post_report(self):
        response1 = self.client.post(self.url, None)
        response2 = self.client.post(self.url, None)
        response3 = self.client.post(self.url, None)

        self.assertEqual(response1.status_code, 201)
        self.assertEqual(response2.status_code, 201)
        self.assertEqual(response3.status_code, 201)

        numPosts = Post.objects.all().count()

        self.assertEqual(numPosts, 1)

        updatedPost = Post.objects.get(postID=self.postID)

        self.assertEqual(updatedPost.numReports, 3)

    def test_post_reports_until_delete(self):
        response1 = self.client.post(self.url, None)
        response2 = self.client.post(self.url, None)
        response3 = self.client.post(self.url, None)
        response4 = self.client.post(self.url, None)
        response5 = self.client.post(self.url, None)

        self.assertEqual(response1.status_code, 201)
        self.assertEqual(response2.status_code, 201)
        self.assertEqual(response3.status_code, 201)
        self.assertEqual(response4.status_code, 201)
        self.assertEqual(response5.status_code, 201)

        numPosts = Post.objects.all().count()

        self.assertEqual(numPosts, 0)