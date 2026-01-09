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
        
    
        full_message = f"""Küresel Turizm web sitesinden yeni mesaj: Ad Soyad: {name} E-posta: {email} Konu: {subject} Mesaj: {message}"""
        
        try:
            
            send_mail(
                subject=f"[Web Sitesi] {subject}",
                message=full_message,
                from_email=settings.DEFAULT_FROM_EMAIL,  
                recipient_list=[settings.DEFAULT_FROM_EMAIL],  
                fail_silently=False,
            )
            
            
            send_mail(
                subject=f"Onay: {subject}",
                message=f"Sayın {name}, mesajınız için teşekkür ederiz. En kısa sürede size dönüş yapacağız.\n\nMesajınız:\n{message}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False,
            )
            
            messages.success(request, "✅ Mesajınız başarıyla gönderildi!")
            
        except Exception as e:
            messages.error(request, "❌ Bir hata oluştu. Lütfen tekrar deneyiniz.")
            
            print(f"E-POSTA HATASI: {e}")
        
        return redirect('core:contact')
    
    return render(request, 'contact.html')