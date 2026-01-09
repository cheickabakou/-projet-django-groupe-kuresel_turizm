from django.urls import path, reverse_lazy
from django.contrib.auth import views as auth_views
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('', views.home_view, name='home'),
    
    
    path('forgot_password/', 
         auth_views.PasswordResetView.as_view(
             template_name="forgot_password.html", 
             email_template_name="password_reset_email.html",  
             subject_template_name="password_reset_subject.txt",
             success_url=reverse_lazy("accounts:password_reset_done"),
             html_email_template_name="password_reset_email.html",  
         ), 
         name="forgot_password"),
    
    path('password_reset_done/', 
         auth_views.PasswordResetDoneView.as_view(
             template_name="password_reset_done.html" 
         ), 
         name="password_reset_done"),
    
    path('reset/<uidb64>/<token>',views.confirm_reset_password,  name="confirm"),  
    
    path('reset_password_complete/', 
         auth_views.PasswordResetCompleteView.as_view(
             template_name="password_reset_complete.html"
         ), 
         name="password_reset_complete"),
]