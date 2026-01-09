from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.contrib.auth import get_user_model
from .forms import CustomUserCreationForm, CustomAuthenticationForm
from .models import UserActivity
import logging

logger = logging.getLogger(__name__)

def register_view(request):
    if request.user.is_authenticated:
        return redirect('visite:index')

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)

            UserActivity.objects.create(
                user=user,
                activity_type='REGISTER',
                ip_address=request.META.get('REMOTE_ADDR'),
                details='Kullanıcı kaydı'
            )

            logger.info(f"Yeni kullanıcı kaydoldu: {user.username}")
            messages.success(request, "Kayıt başarılı!")
            return redirect('visite:index')
    else:
        form = CustomUserCreationForm()

    return render(request, 'register.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('visite:index')

    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)

            UserActivity.objects.create(
                user=user,
                activity_type='LOGIN',
                ip_address=request.META.get('REMOTE_ADDR'),
                details='Kullanıcı giriş yaptı'
            )

            logger.info(f"Kullanıcı giriş yaptı: {user.username}")
            next_url = request.POST.get('next')
            return redirect(next_url or 'visite:index')
        else:
            messages.error(request, "Geçersiz kullanıcı adı veya şifre")
    else:
        form = CustomAuthenticationForm()

    return render(request, 'login.html', {'form': form})

@login_required
def logout_view(request):
    UserActivity.objects.create(
        user=request.user,
        activity_type='LOGOUT',
        ip_address=request.META.get('REMOTE_ADDR'),
        details='Kullanıcı çıkış yaptı'
    )
    logger.info(f"Kullanıcı çıkış yaptı: {request.user.username}")
    logout(request)
    messages.info(request, "Oturumunuz kapatıldı")
    return redirect('accounts:login')

def forgot_password_view(request):
    User = get_user_model()
    
    if request.method == 'POST':
        email = request.POST.get('email')
        users = User.objects.filter(email=email)

        if users.exists():

            request.session['reset_email'] = email
            messages.success(
                request,
                "✓ Şifre sıfırlama bağlantısı e-posta adresinize gönderildi."
            )

            return redirect('accounts:reset_password')
        
        else:
            messages.error(
                request,
                "✗ Bu e-posta adresi kayıtlı değil."
            )
            return redirect('accounts:forgot_password')

    return render(request, 'forgot_password.html')

def password_reset_done_view(request):
    return render(request, 'password_reset_done.html')

def reset_password_view(request):
    if request.user.is_authenticated:
        return redirect('visite:index')
    
    User = get_user_model()


    reset_email = request.session.get('reset_email')
    
    if not reset_email:
        messages.error(request, "Geçersiz şifre sıfırlama talebi!")
        return redirect('accounts:forgot_password')
    

    try:
        user = User.objects.get(email=reset_email)
    except User.DoesNotExist:
        messages.error(request, "Kullanıcı bulunamadı!")
        return redirect('accounts:forgot_password')
    
    if request.method == 'POST':
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        

        if not new_password or not confirm_password:
            messages.error(request, "Lütfen tüm alanları doldurun!")
            return render(request, 'reset_password.html')
        
        if new_password != confirm_password:
            messages.error(request, "Şifreler uyuşmuyor!")
            return render(request, 'reset_password.html')
        
        if len(new_password) < 6:
            messages.error(request, "Şifre en az 6 karakter olmalı!")
            return render(request, 'reset_password.html')
        
        user.set_password(new_password)
        user.save()
        

        if 'reset_email' in request.session:
            del request.session['reset_email']
        

        UserActivity.objects.create(
            user=user,
            activity_type='PASSWORD_CHANGE',
            ip_address=request.META.get('REMOTE_ADDR'),
            details='Şifre sıfırlama işlemi'
        )
        
        logger.info(f"Kullanıcının şifresi sıfırlandı: {user.username}")
        messages.success(request, "✅ Şifreniz başarıyla değiştirildi!")
        return redirect('accounts:password_reset_complete')
    
    return render(request, 'reset_password.html')

def password_reset_complete_view(request):
    return render(request, 'password_reset_complete.html')

@login_required
def profile_view(request):
    if request.method == 'POST':
        updated = False
        username = request.POST.get('username')
        email = request.POST.get('email')
        
        if username and username != request.user.username:
            request.user.username = username
            updated = True
        
        if email and email != request.user.email:
            request.user.email = email
            updated = True
        
        if updated:
            request.user.save()
            UserActivity.objects.create(
                user=request.user,
                activity_type='PROFILE_UPDATE',
                ip_address=request.META.get('REMOTE_ADDR'),
                details='Profil güncellendi'
            )
            messages.success(request, "Profil başarıyla güncellendi")
        
        return redirect('accounts:profile')
    
    recent_activities = UserActivity.objects.filter(user=request.user)[:5]
    return render(request, 'profile.html', {
        'user': request.user,
        'recent_activities': recent_activities
    })

def confirm_reset_password(request, uidb64=None, token=None):

    if request.user.is_authenticated:
        return redirect('visite:index')
    
    User = get_user_model()
    

    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except:
        user = None
    

    if user is None or not default_token_generator.check_token(user, token):
        messages.error(request, "Geçersiz veya süresi dolmuş bağlantı!")
        return redirect('accounts:forgot_password')
    
    if request.method == 'POST':


        password = request.POST.get('password')
        confirm = request.POST.get('confirm_password')
        

        if not password or not confirm:
            messages.error(request, "Lütfen her iki alanı da doldurun!")
        elif password != confirm:
            messages.error(request, "Şifreler uyuşmuyor!")
        elif len(password) < 6:
          
            messages.error(request, "Şifre en az 6 karakter uzunluğunda olmalıdır!")
        else:
            
            user.set_password(password)
            user.save()
            messages.success(request, "✅ Şifre başarıyla değiştirildi!")
            return redirect('accounts:login')
    
    return render(request, 'reset_password.html', {
        'uidb64': uidb64,
        'token': token,
        'validlink': True
    })

def home_view(request):
    if request.user.is_authenticated:
        return redirect('visite:index')
    return redirect('accounts:login')