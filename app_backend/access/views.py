import sys

from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse

# Create your views here.

@csrf_exempt
def access(request):
    try:
        if request.method == "GET":
            if request.GET['accessCode'] == "access-token12":
                return JsonResponse({'accessGranted': True})
            else:
                return JsonResponse({'accessGranted': False})

    except:
        print(" [ERROR]", sys.exc_info())
        return HttpResponse(status=500)