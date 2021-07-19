from django.test import TestCase
from django.urls import reverse

# Create your tests here.

class TestAccessToken(TestCase):
    def setUp(self):
        self.url = reverse('access')

    def test_correct_access_code(self):
        response = self.client.get(self.url + '?accessToken=aCCESS_tOKEN1010zaq7710_1122')

        self.assertEqual(response.status_code, 200)

    def test_incorrect_access_code(self):
        response1 = self.client.get(self.url + '?accessToken=')
        response2 = self.client.get(self.url + '?accessToken=ababsdasnasd')
        response3 = self.client.get(self.url + '?accessToken=ababadsbn1sdasnasd')
        response4 = self.client.get(self.url + '?accessToken=aCCESS_tOKEN1010zaq7710_11221')
        response5 = self.client.get(self.url + '?accessToken=aCCESS_tOKeN1010zaq7710_1122')

        self.assertEqual(response1.status_code, 400)
        self.assertEqual(response2.status_code, 400)
        self.assertEqual(response3.status_code, 400)
        self.assertEqual(response4.status_code, 400)
        self.assertEqual(response5.status_code, 400)