from django.http import HttpResponse
#path setting

def hello(request):
    return HttpResponse("Hello welcome to Django")

def thankYou(request):
    return HttpResponse("Thank you from Django")