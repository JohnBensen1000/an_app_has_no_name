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
WatchedBy     = apps.get_model("models", "Following")

class TestRecordWatched(BaseTest):
    def setUp(self):
        self.cleint = Client()

    def test_record_watched(self):
        user1 = self.create_user_object('test1', 'test1')
        user2 = self.create_user_object('test2', 'test2')

        post = self.create_post_object(user1)

        url      = reverse('watched', kwargs={'postID': post.postID})
        response = self.client.post(
            url,
            json.dumps({
                "uid": user2.uid,
                "userRating": 1,
            }),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)
        # self.assertEqual(WatchedBy.objects.count(), 1)
        # self.assertEqual(WatchedBy.objects.first().user.uid, user2.uid)