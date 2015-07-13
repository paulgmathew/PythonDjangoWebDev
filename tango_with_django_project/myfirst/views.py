# Create your views here.
from django.http import HttpResponse

def first(request):
    return HttpResponse("Rango says come to my application")