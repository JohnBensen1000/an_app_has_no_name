from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt

from google.oauth2 import id_token
from google.auth.transport import requests

from user_profile.models import UserProfile, AccountInfo, Relationships

# Create your views here.
@csrf_exempt
def authentication(request):
    try:
        # Recieves two tokens: deviceToken and idToken. deviceToken is used to identify the physical device
        # that they user is using the app on (needed for messaging). idToken, after being decoded, contains 
        # information about a user's Firebase account. idToken["sub"] is used to identify the database's
        # userProfile entity associated with the user's Firebase account. When the correct userProfile is
        # found, updates the userProfile.deviceToken field and returns the userID and an authentication token. 
        # TODO: Actually make authToken secure. 
        if request.method == "POST":
            deviceToken = request.POST["deviceToken"]
            idToken     = request.POST["idToken"]

            idInfo      = id_token.verify_firebase_token(idToken, requests.Request())
            userProfile = UserProfile.objects.get(firebaseSub=idInfo["sub"])
            userProfile.deviceToken = deviceToken
            userProfile.save()

            return JsonResponse({"userID": userProfile.userID, "authToken": "12345"})

    except:
        print(" [ERROR]", sys.exc_info()[0])
        return HttpResponse(status=500)
