import json
import sys

from django.test import TestCase, Client, client
from django.urls import reverse
from django.apps import apps

User        = apps.get_model("models", "User")
Preferences = apps.get_model("models", "Preferences")
Profile     = apps.get_model("models", "Profile")

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
        self.assertEqual(response.status_code, 200)
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
        self.assertEqual(response.status_code, 200)
        self.assertEqual(updatedUser.signedIn, True)
        self.assertEqual(updatedUser.deviceToken, deviceToken2)

    def test_sign_out(self):
        response = self.client.post(
            self.url, 
            json.dumps({
                'signIn': False
            }), 
            content_type='application/json'
        )

        updatedUser = User.objects.get(uid=self.uid)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(updatedUser.signedIn, False)
        self.assertEqual(updatedUser.deviceToken, "")

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
        self.assertEqual(responseBody['uid'], self.uid)

