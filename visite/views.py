from django.shortcuts import render

def index(request):
    return render(request, 'index.html')

def destinations(request):
    return render(request, 'destinations.html')