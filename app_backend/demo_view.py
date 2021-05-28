''' 
    try:
        if request.method == "GET":
            pass

        if request.method == "POST":
            pass

        if request.method == "DELETE":
            pass

    except:
        print(" [ERROR]", sys.exc_info())
        return HttpResponse(status=500)
'''