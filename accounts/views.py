from django.shortcuts import render, redirect
from django.contrib import messages
from django.template.loader import render_to_string
from django.conf import settings
import random
import string

FAKE_USERS_DB = {
    'brenda': {
        'password': 'admin123',
        'email': 'brenda@gmail.com',
        'first_name': 'brenda',
        'last_name': 'User',
        'user_name':'brenda',
    },
    'test': {
        'password': 'test123', 
        'email': 'test@example.com',
        'first_name': 'Test',
        'last_name': 'User'
    }
}

RESET_TOKENS = {}


def login_view(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        if username in FAKE_USERS_DB and FAKE_USERS_DB[username]['password'] == password:
            request.session['is_logged_in'] = True
            request.session['username'] = username
            request.session['user_data'] = FAKE_USERS_DB[username]
            
            messages.success(request, f"Hoş geldiniz {FAKE_USERS_DB[username]['first_name']}! ")
            return redirect('anasayfa')
        
        messages.error(request, "Kullanıcı adı veya şifre hatalı!")

    return render(request, "login.html")

def register_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")
        
        if password != confirm_password:
            messages.error(request, "Şifreler uyuşmuyor! ")
            return render(request, "register.html")
        
        if username in FAKE_USERS_DB:
            messages.error(request, "Bu kullanıcı adı zaten alınmış! ")
            return render(request, "register.html")
        
        for user_data in FAKE_USERS_DB.values():
            if user_data['email'] == email:
                messages.error(request, "Bu email adresi zaten kayıtlı! ")
                return render(request, "register.html")
        try:
            FAKE_USERS_DB[username] = {
                'password': password,
                'email': email,
                'first_name': first_name,
                'last_name': last_name
            }
            request.session['is_logged_in'] = True
            request.session['username'] = username
            request.session['user_data'] = FAKE_USERS_DB[username]
            messages.success(request, f"Hoş geldiniz {first_name}! KURESEL TURİZM'e kaydoldunuz! 🎉")
            return redirect('anasayfa')
        
        except Exception as e:
            messages.error(request, "Bir hata oluştu, lütfen tekrar deneyin! ❌")

    return render(request, "register.html")

def logout_view(request):
    if request.session.get('is_logged_in'):
        user_name = request.session.get('user_data', {}).get('first_name', 'Ziyaretçi')
        request.session.flush()
        messages.info(request, f"Güle güle {user_name}! Tekrar bekleriz! 👋")
    else:
        messages.warning(request, "Zaten çıkış yapmışsınız!")
    return redirect('anasayfa')

def forgot_password_view(request):
    if request.method == "POST":
        email = request.POST.get('email', '').strip()
        
        user_found = None
        user_data_found = None
        
        for username, user_data in FAKE_USERS_DB.items():
            if user_data['email'] == email:
                user_found = username
                user_data_found = user_data
                break
        
        if user_found:
            token = ''.join(random.choices(string.ascii_letters + string.digits, k=32))
            RESET_TOKENS[token] = {
                'username': user_found,
                'email': email
            }
            
            reset_url = f"http://{request.get_host()}/accounts/reset-password/{token}/"
            
            context = {
                'user': {
                    'first_name': user_data_found['first_name'],
                    'last_name': user_data_found['last_name'],
                    'email': email
                },
                'reset_url': reset_url,
                'site_name': 'Küresel Turizm',
                'protocol': 'http',
                'domain': request.get_host(),
            }
            
            subject = render_to_string('password_reset_subject.txt', context)
            subject = ''.join(subject.splitlines()) 
            
            html_message = render_to_string('password_reset_email.html', context)
            plain_message = render_to_string('password_reset_email.txt', context)
            
            if settings.DEBUG:
                print("="*60)
                print("📧 EMAIL DE RÉINITIALISATION SIMULÉ")
                print("="*60)
                print(f"À: {email}")
                print(f"SUJET: {subject}")
                print(f"LIEN DE RÉINITIALISATION: {reset_url}")
                print("-"*60)
                print("CONTENU HTML (extrait):")
                print(html_message[:500] + "...")
                print("="*60)
            
            messages.success(request, 
                f"📨 <strong>Şifre sıfırlama e-postası hazırlandı!</strong><br><br>"
                f"<strong>Alıcı:</strong> {email}<br>"
                f"<strong>Konu:</strong> {subject}<br>"
                f"<strong>Demo Link:</strong> <a href='{reset_url}' target='_blank'>{reset_url}</a><br><br>"
                f"💡 <em>Demo modu: Gerçek e-posta gönderilmez. Yukarıdaki linke tıklayarak devam edebilirsiniz.</em>"
            )
            
            request.session['demo_reset_token'] = token
            
            return redirect('password_reset_done')
        else:
            messages.error(request, 
                "❌ <strong>Bu e-posta adresi kayıtlı değil!</strong><br>"
                "Lütfen kayıt olurken kullandığınız e-posta adresini girin."
            )
    
    return render(request, "forgot_password.html")

def password_reset_done_view(request):
    token = request.session.get('demo_reset_token', 'DEMO_TOKEN_123')
    reset_url = f"http://{request.get_host()}/accounts/reset-password/{token}/"
    
    context = {
        'reset_url': reset_url
    }
    
    return render(request, "password_reset_done.html", context)

def reset_password_view(request, token=None):
    
    if token:
        if token not in RESET_TOKENS and token != 'DEMO_TOKEN_123':
            messages.error(request, "❌ Geçersiz veya süresi dolmuş bağlantı!")
            return redirect('forgot_password')
        
        if token == 'DEMO_TOKEN_123' or token in RESET_TOKENS:
            request.session['valid_reset_token'] = token
    
    if request.method == "POST":
        new_password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        
        token = request.POST.get('token') or request.session.get('valid_reset_token')

        if new_password != confirm_password:
            messages.error(request, " Şifreler uyuşmuyor!")
        elif len(new_password) < 6:
            messages.error(request, " Şifre en az 6 karakter olmalı!")
        else:
            if token and token in RESET_TOKENS:
                username = RESET_TOKENS[token]['username']
                FAKE_USERS_DB[username]['password'] = new_password
                del RESET_TOKENS[token]
            
            if 'valid_reset_token' in request.session:
                del request.session['valid_reset_token']
            if 'demo_reset_token' in request.session:
                del request.session['demo_reset_token']
            
            messages.success(request, 
                "✅ <strong>Şifreniz başarıyla 'güncellendi'!</strong><br>"
                "Artık yeni şifrenizle giriş yapabilirsiniz.<br>"
                "💡 <em>Demo modu: Gerçekte şifre veritabanında güncellenir.</em>"
            )
            return redirect('password_reset_complete')
    
    context = {
        'token': token or request.session.get('valid_reset_token', '')
    }
    
    return render(request, "reset_password.html", context)

def password_reset_complete_view(request):
    return render(request, "password_reset_complete.html")

def anasayfa_view(request):
    is_logged_in = request.session.get('is_logged_in', False)
    user_data = request.session.get('user_data', {})
    
    context = {
        'is_logged_in': is_logged_in,
        'user': user_data,
        'username': request.session.get('username', '')
    }
    return render(request, 'anasayfa.html', context)