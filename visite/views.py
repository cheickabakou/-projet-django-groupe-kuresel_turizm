from django.shortcuts import render

def index(request):
    return render(request, 'index.html')

def destinations(request):
    destinations_list = [
        {'nom': 'Paris, France', 'prix': 398, 'jours': 10},
        {'nom': 'Ankara, Turquie', 'prix': 550, 'jours': 7},
        {'nom': 'Tokyo, Japon', 'prix': 1200, 'jours': 14},
    ]
    
    return render(request, 'destinations.html', {
        'destinations': destinations_list
    })

def reservation(request):
    destination = request.GET.get('dest', 'Paris, France')
    prix = request.GET.get('prix', '398')
    jours = request.GET.get('jours', '10')
    
    return render(request, 'reservation.html', {
        'destination': destination,
        'prix': prix,
        'jours': jours 
    })