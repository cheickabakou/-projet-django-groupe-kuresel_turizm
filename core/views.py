from django.shortcuts import render, redirect
from django.contrib import messages

def home(request):
    return render(request, 'home.html')

def about(request):
    return render(request, 'about.html')

def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')
        
        if name and email and message:
            messages.success(request, f"Merci {name}! Votre message a été envoyé. ")
            return redirect('contact')
        else:
            messages.error(request, "Veuillez remplir tous les champs.")
    
    return render(request, 'contact.html')