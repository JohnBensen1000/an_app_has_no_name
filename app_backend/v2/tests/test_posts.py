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

class TestPosts(BaseTest):
    def setUp(self):
        self.user   = self.create_user_object('test', 'test')
        self.cleint = Client()

    def test_upload_post(self):
        '''
            Tests to see if uploading a post creates a new post object with the correct values
            for each field. 
        '''
        downloadURL = "https://00f74ba44bf829ce4e16646453f495bb10ef7eb2cd-apidata.googleusercontent.com/download/storage/v1/b/entropy-develop.appspot.com/o/USERS%2F0kmSxwCdhJfbgc637gJydFCL13q1%2F1627306278547290.jpg?jk=AFshE3WcEICJFs50lwsH_Lzm812PsDE-7lKpQl4Ws6qdJuo3NAtspvP2tCvn7yYTDzpMgfSMMnNT2GHqMrtxBCcbkPaeOeO2Hh59Vtfw4peo6GVTadtiwwnJtv9SytXtQUQWBOb73NF6S0tgtZBASKtkOHJu7B-Lu5rmP6sfCaChMekM7NtBMpj-Pdi4vyGeO0OEPlEam5sr5S96hXMFiyMBERRyC89YxwEKghY-faNjL8GcOHEjavAtP2OHtMzImizHzJReEpzNEfvzeKmW9XRz1dc2QJg1CIBsj5UFiFJGHeu-k09wxqGZaSps6DC9FyxxBGucHFlzyni1U5mdhNMCA-_JfzdK9vr3bPOv9Tt7nyH0poOp9bemq1EZoG3AkHj5OTsz3ZEX0Xmt40NZsfi3PLaflrK1QCqtxfAIjxmlXkhttmlzS03q7b58dRI44GSl8c9rYbEs9jI_CK5H9rx_2s2NUHHqPjepYUkZSIH13gGENYp2oHEHTElw0HuH4FhvtpvoyJSS05L5DP7D7RbuN3ZQLImLg4DNh40oGwaRadAw2wR9Kl_N-nIJDkz_xseyJBPxWbZPoZf_i4B4rnlPasBW99aDtJKc6mOHN7Ef9ecJ4xptH-W5nZVByQSMerXZwGB-kFMSt3KSTk5A9U1lkiINV4OZyLEgV_772t_1mdnD51ouRDYJhmT6l0nf0OZYGVC0HqLPnRdPwFMnKs3IhDAxvuD8MIss36cfRuvBUs01jq5CkPydXSJ-qtWkozOJYGM3orA_jXhNMoWUxIcj6Gnv4f9nJyW2x--bhg60FWXen_SxtjLIyhgWO5eDawCl6qSUVq3UOfCyiv1ByWwx1RFBNBbWCiOJttLuvVipgzcvdEh5zv5Xc_zEqBeLsmjKI5XvVs_tguvae3V8j19Hwl4Et0X8AAThBJcPNwZ2jIyjGtOrPfoPdiQUCwACk0B6u0ERBf3c_G7UAKyow0Zj4RUHau9E4xoPAFaaz7UZgeO19SyAXO0P46cabvcwgFs7Av5yFhdu6w24hwf6Jng&isca=1"
        url         = reverse('posts', kwargs={'uid': self.user.uid})
        response    = self.client.post(
            url, 
            json.dumps({
                'isPost':   True,
                'isImage':  True,
                'isPrivate': True,
                'downloadURL': downloadURL
            }),
            content_type='application/json'
        )

        post = Post.objects.first()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(post.creator.uid, self.user.uid)
        self.assertEqual(post.isImage, True)
        self.assertEqual(post.isPrivate, True)   

    def test_get_posts(self):
        '''
            Tests if getting a user's list of posts returns all the posts that the user has
            posted that are not flagged as inappropriate. For this test, only post3 is flagged
            is inappropriate.
        '''
        post1 = Post.objects.create(
            postID      = '1234',
            isPrivate   = False,
            isImage     = False,
            downloadURL = "5454",
            preferences = Preferences.objects.create(),
            creator     = self.user
        )
        post2 = Post.objects.create(
            postID      = '12123234',
            isPrivate   = False,
            isImage     = False,
            downloadURL = "544554",
            preferences = Preferences.objects.create(),
            creator     = self.user
        )
        post3 = Post.objects.create(
            postID      = '12432334',
            isPrivate   = False,
            isImage     = True,
            downloadURL = "54243554",
            preferences = Preferences.objects.create(),
            creator     = self.user,
        )
        post4 = Post.objects.create(
            postID      = '1243111134',
            isPrivate   = False,
            isImage     = True,
            downloadURL = "54243554",
            preferences = Preferences.objects.create(),
            creator     = self.user
        )

        post3.isFlagged = True
        post3.save()

        url          = reverse('posts', kwargs={'uid': self.user.uid})
        response     = self.client.get(url)
        responseBody = json.loads(response.content)
        postIDs      = [postJson['postID'] for postJson in responseBody['posts']]

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(responseBody['posts']), 3)
        
        self.assertTrue(post1.postID in postIDs)
        self.assertTrue(post2.postID in postIDs)
        self.assertTrue(post4.postID in postIDs)
        self.assertFalse(post3.postID in postIDs)

    def test_post_profile(self):
        downloadURL = "https://00f74ba44bf829ce4e16646453f495bb10ef7eb2cd-apidata.googleusercontent.com/download/storage/v1/b/entropy-develop.appspot.com/o/USERS%2F0kmSxwCdhJfbgc637gJydFCL13q1%2F1627306278547290.jpg?jk=AFshE3WcEICJFs50lwsH_Lzm812PsDE-7lKpQl4Ws6qdJuo3NAtspvP2tCvn7yYTDzpMgfSMMnNT2GHqMrtxBCcbkPaeOeO2Hh59Vtfw4peo6GVTadtiwwnJtv9SytXtQUQWBOb73NF6S0tgtZBASKtkOHJu7B-Lu5rmP6sfCaChMekM7NtBMpj-Pdi4vyGeO0OEPlEam5sr5S96hXMFiyMBERRyC89YxwEKghY-faNjL8GcOHEjavAtP2OHtMzImizHzJReEpzNEfvzeKmW9XRz1dc2QJg1CIBsj5UFiFJGHeu-k09wxqGZaSps6DC9FyxxBGucHFlzyni1U5mdhNMCA-_JfzdK9vr3bPOv9Tt7nyH0poOp9bemq1EZoG3AkHj5OTsz3ZEX0Xmt40NZsfi3PLaflrK1QCqtxfAIjxmlXkhttmlzS03q7b58dRI44GSl8c9rYbEs9jI_CK5H9rx_2s2NUHHqPjepYUkZSIH13gGENYp2oHEHTElw0HuH4FhvtpvoyJSS05L5DP7D7RbuN3ZQLImLg4DNh40oGwaRadAw2wR9Kl_N-nIJDkz_xseyJBPxWbZPoZf_i4B4rnlPasBW99aDtJKc6mOHN7Ef9ecJ4xptH-W5nZVByQSMerXZwGB-kFMSt3KSTk5A9U1lkiINV4OZyLEgV_772t_1mdnD51ouRDYJhmT6l0nf0OZYGVC0HqLPnRdPwFMnKs3IhDAxvuD8MIss36cfRuvBUs01jq5CkPydXSJ-qtWkozOJYGM3orA_jXhNMoWUxIcj6Gnv4f9nJyW2x--bhg60FWXen_SxtjLIyhgWO5eDawCl6qSUVq3UOfCyiv1ByWwx1RFBNBbWCiOJttLuvVipgzcvdEh5zv5Xc_zEqBeLsmjKI5XvVs_tguvae3V8j19Hwl4Et0X8AAThBJcPNwZ2jIyjGtOrPfoPdiQUCwACk0B6u0ERBf3c_G7UAKyow0Zj4RUHau9E4xoPAFaaz7UZgeO19SyAXO0P46cabvcwgFs7Av5yFhdu6w24hwf6Jng&isca=1"
        url         = reverse('profile', kwargs={'uid': self.user.uid})
        response    = self.client.post(
            url, json.dumps({
                'isImage':  True,
                'downloadURL': downloadURL
            }),
            content_type='application/json'
        )

        user = User.objects.get(uid=self.user.uid)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Profile.objects.count(), 1)
        self.assertTrue(user.profile.exists)

    def test_get_users_profile(self):
        url      = reverse('profile', kwargs={'uid': self.user.uid})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

    def test_delete_post(self):
        post     = self.create_post_object(self.user)
        url      = reverse('post', kwargs={'uid': self.user.uid, 'postID': post.postID})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Post.objects.count(), 0)
