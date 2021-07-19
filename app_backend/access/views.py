from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse

# Create your views here.

@csrf_exempt
def access(request):
    try:
        if request.method == "GET":
            accessToken = request.GET['accessToken']
            if accessToken == "aCCESS_tOKEN1010zaq7710_1122":
                return HttpResponse(status=200)
            else:
                return HttpResponse(status=400)

    except:
        print(" [ERROR]", sys.exc_info())
        return HttpResponse(status=500)