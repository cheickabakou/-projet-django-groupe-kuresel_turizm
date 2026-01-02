from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings

def home(request):
    return render(request, 'home.html')

def about(request):
    return render(request, 'about.html')

def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        
        # Construire le message
        full_message = f"""
        Nouveau message depuis le site Küresel Turizm:
        
        Nom: {name}
        Email: {email}
        Sujet: {subject}
        
        Message:
        {message}
        """
        
        try:
            # FORME CLASSIQUE - Django utilise les paramètres de settings.py
            send_mail(
                subject=f"[Site Web] {subject}",
                message=full_message,
                from_email=settings.DEFAULT_FROM_EMAIL,  # ← Django remplace automatiquement
                recipient_list=[settings.DEFAULT_FROM_EMAIL],  # ← Envoie à l'agence
                fail_silently=False,
            )
            
            # Copie à l'utilisateur (optionnel)
            send_mail(
                subject=f"Confirmation: {subject}",
                message=f"Merci {name} pour votre message. Nous vous répondrons sous peu.\n\nVotre message:\n{message}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False,
            )
            
            messages.success(request, "✅ Message envoyé avec succès !")
            
        except Exception as e:
            # Message générique pour l'utilisateur
            messages.error(request, "❌ Une erreur est survenue. Veuillez réessayer.")
            # Mais on log l'erreur réelle
            print(f"ERREUR EMAIL: {e}")
        
        return redirect('core:contact')
    
    return render(request, 'contact.html')