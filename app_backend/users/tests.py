import json

from django.test import TestCase, Client, client
from django.urls import reverse
from django.apps import apps

User        = apps.get_model("models", "User")
Preferences = apps.get_model("models", "Preferences")
Profile     = apps.get_model("models", "Profile")

class TestNewUser(TestCase):
    def setUp(self):
        self.client = Client()
        self.url    = reverse('new_user')   

    def test_create_account(self):
        newUserJson = {
            'userID': 'Laura1000',
            'phone': '5164979872',
            'email': 'email@gmail.com',
            'uid': 'laura1313',
            'username': 'Laura Hayes',
        }
        response = self.client.post(self.url, json.dumps(newUserJson), content_type='application/json')

        user = User.objects.first()
        
        self.assertEqual(response.status_code, 201)
        self.assertEqual(user.userID, 'Laura1000')
        self.assertEqual(user.phone,  '5164979872')
        self.assertEqual(user.email,  'email@gmail.com')
        self.assertEqual(user.uid, 'laura1313')
        self.assertEqual(user.username, 'Laura Hayes')

    def test_unique_fields_taken(self):
        User.objects.create(
            userID      = 'Laura1000',
            email       = 'email@gmail.com',
            phone       = '5164979872',
            uid         = 'laura1313',
            username    = 'Laura Hayes',
            preferences = Preferences.objects.create(),
            profile     = Profile.objects.create(),
        )

        newUserJson1 = {
            'userID': 'Laura1000',
            'phone': '5164979872',
            'email': 'email@gmail.com',
            'uid': 'laura1313',
            'username': 'Laura Hayes',
        }
        newUserJson2 = {
            'userID': 'Laura10',
            'phone': '1111112222',
            'email': 'email@gmail.com',
            'uid': 'laura1313',
            'username': 'Laura Hayes',
        }
        newUserJson3 = {
            'userID': 'Laura1000',
            'phone': '1212',
            'email': 'email@gmail.com',
            'uid': 'john1234',
            'username': 'Laura Hayes',
        }
        response1 = self.client.post(self.url, json.dumps(newUserJson1), content_type='application/json')
        response2 = self.client.post(self.url, json.dumps(newUserJson2), content_type='application/json')
        response3 = self.client.post(self.url, json.dumps(newUserJson3), content_type='application/json')

        self.assertEqual(response1.status_code, 400)
        self.assertEqual(response2.status_code, 400)
        self.assertEqual(response3.status_code, 400)

        body1 = json.loads(response1.content)["alreadyTaken"]
        body2 = json.loads(response2.content)["alreadyTaken"]
        body3 = json.loads(response3.content)["alreadyTaken"]

        self.assertEqual(body1, ["userID", "email", "phone", "uid"])
        self.assertEqual(body2, ["email", "uid"])
        self.assertEqual(body3, ["userID", "email"])

class TestSearch(TestCase):
    def setUp(self):
        self.client = Client()
        self.url    = reverse('search')

    def test_search_strings(self):
        user1 = {'userID': "John1000", 'username': "john"}
        user2 = {'userID': "Laura",    'username': "Laura Hayes"}
        user3 = {'userID': "Andrew",   'username': "andrew"}
        user4 = {'userID': "Andrew11", 'username': "andrew"}
        user5 = {'userID': "jake",     'username': "jake"}
   
        self._create_user_object(user1)
        self._create_user_object(user2)
        self._create_user_object(user3)
        self._create_user_object(user4)
        self._create_user_object(user5)

        responseBody1 = json.loads(self.client.get(self.url + '?contains=john').content)
        responseBody2 = json.loads(self.client.get(self.url + '?contains=a').content)
        responseBody3 = json.loads(self.client.get(self.url + '?contains=andrew').content)
        responseBody4 = json.loads(self.client.get(self.url + '?contains=').content)
        responseBody5 = json.loads(self.client.get(self.url + '?contains=JacobChen').content)

        self.assertEquals(len(responseBody1['creatorsList']), 1)
        self.assertEquals(len(responseBody2['creatorsList']), 4)
        self.assertEquals(len(responseBody3['creatorsList']), 2)
        self.assertEquals(len(responseBody4['creatorsList']), 0)
        self.assertEquals(len(responseBody5['creatorsList']), 0)

    def _create_user_object(self, user):
        User.objects.create(
            userID   = user['userID'],
            email    = user['userID'] + '@gmail.com',
            phone    = user['userID'] + '12345',
            username = user['username'],
            preferences = Preferences.objects.create(),
            profile     = Profile.objects.create(),
            uid         = user['userID'] + user['username']
        )

class TestUser(TestCase):
    def setUp(self):
        self.userID   = 'Laura1000'
        self.username = 'Laura Hayes'
        self.email    = 'laura@gmail.com'
        self.phone    = '5164979872'
        self.uid      = 'laura1313'

        self.client = Client()
        self.url    = '/v1/users/' + self.uid + '/'

        self.user = User.objects.create(
            userID      = self.userID,
            email       = self.email,
            phone       = self.phone,
            uid         = self.uid,
            username    = self.username,
            preferences = Preferences.objects.create(),
            profile     = Profile.objects.create(),
        )

    def test_get_user(self):   
        response = self.client.get(self.url)
        bodyJson = json.loads(response.content)

        self.assertEqual(response.status_code, 200)

        self.assertEqual(bodyJson['userID'],   self.userID)
        self.assertEqual(bodyJson['username'], self.username)
        self.assertEqual(bodyJson['email'],    self.email)
        self.assertEqual(bodyJson['phone'],    self.phone)

    def test_update_user_fields(self):
        newEmail    = 'newLaura@gmail.com'
        newPhone    = '123456789'
        newUsername = 'Laura'

        newData = {
            'email':    newEmail,
            'phone':    newPhone,
            'username': newUsername
        }
        response    = self.client.post(self.url, json.dumps(newData), content_type='application/json')
        updatedUser = User.objects.get(userID=self.userID)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(updatedUser.email, newEmail)
        self.assertEqual(updatedUser.phone, newPhone)
        self.assertEqual(updatedUser.username, newUsername)

    def test_update_user_fields_when_fields_are_taken(self):
        email = 'john@gmail.com'
        phone = '12345'

        User.objects.create(
            userID   = 'john',
            email    = email,
            phone    = phone,
            username = 'john bensen',
            preferences = Preferences.objects.create(),
            profile     = Profile.objects.create(),
        )

        newData = {
            'email':    email,
            'phone':    phone,
            'username': 'Laura'
        }

        response    = self.client.post(self.url, json.dumps(newData), content_type='application/json')
        bodyJson    = json.loads(response.content)
        updatedUser = User.objects.get(userID=self.userID)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(bodyJson, {"alreadyTaken": ["email", "phone"]})
        self.assertEqual(updatedUser.email, self.email)
        self.assertEqual(updatedUser.phone, self.phone)
        self.assertEqual(updatedUser.username, self.username)

    def test_delete_user(self):
        response = self.client.delete(self.url)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.filter(userID=self.userID).exists(), False)
        self.assertEqual(Preferences.objects.count(), 0)
        self.assertEqual(Profile.objects.count(), 0)
