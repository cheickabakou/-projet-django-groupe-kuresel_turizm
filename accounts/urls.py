from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.login_view, name="login"),
    path('register/',views.register_view,name="register"),
    path('logout/',views.logout_view,name="logout"),
    path('forgot-password/', views.forgot_password_view, name="forgot_password"),
    path('password-reset/done/', views.password_reset_done_view, name="password_reset_done"),
    path('reset-password/', views.reset_password_view, name="reset_password"),
    path('password-reset/complete/', views.password_reset_complete_view, name="password_reset_complete"),
]