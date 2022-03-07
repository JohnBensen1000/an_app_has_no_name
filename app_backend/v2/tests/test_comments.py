import json

from django.test import TestCase, Client, client
from django.urls import reverse
from django.apps import apps

from .test import BaseTest

import methods.firestore_helpers as firestore_helpers

import firebase_admin
from firebase_admin import auth
from google.cloud import firestore

db = firestore.Client()

User          = apps.get_model("models", "User")
Preferences   = apps.get_model("models", "Preferences")
Profile       = apps.get_model("models", "Profile")
Blocked       = apps.get_model("models", "Blocked")
ChatMember    = apps.get_model("models", "ChatMember")
Chat          = apps.get_model("models", "Chat")
Post          = apps.get_model("models", "Post")

class CommentsTest(BaseTest):
    def setUp(self):
        self.user   = self.create_user_object('test', 'test')
        self.client = Client()

        self.post = Post.objects.create(
            postID      = '12345',
            isPrivate   = False,
            isImage     = False,
            downloadURL = "5454",
            preferences = Preferences.objects.create(),
            creator     = self.user
        )
        self.commentPath = self.upload_comments()

    def tearDown(self):
        commentDocRef = db.document('COMMENTS' + "/%s" % self.post.postID)
        firestore_helpers.delete_document_and_sub_collections(commentDocRef)

    def upload_comments(self):
        url       = reverse('comments', kwargs={'postID': self.post.postID})
        response1 = self.client.post(
            url, 
            json.dumps({
                "path": "",
                'comment':  "test comment 1",
                'uid': self.user.uid
            }),
            content_type='application/json'
        )
        response2 = self.client.post(
            url, 
            json.dumps({
                "path": json.loads(response1.content)["path"],
                'comment':  "test comment 2",
                'uid': self.user.uid
            }),
            content_type='application/json'
        )
        self.client.post(
            url, 
            json.dumps({
                "path": json.loads(response2.content)["path"],
                'comment':  "test comment 3",
                'uid': self.user.uid
            }),
            content_type='application/json'
        )
        return json.loads(response2.content)["path"]

    def test_delete_comment(self):
        url = reverse('comments', kwargs={'postID': self.post.postID})

        response = self.client.delete(
            url, 
            json.dumps({
                'path': self.commentPath
            }),
            content_type='application/json'
        )

        commentDocRef = db.document('COMMENTS/' + self.post.postID + self.commentPath)

        self.assertEqual(response.status_code, 200)
        self.assertIsNone(commentDocRef.get().to_dict())