from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, UserActivity

class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'email', 'phone', 'is_staff', 'is_active']
    list_filter = ['is_staff', 'is_active']
    search_fields = ['username', 'email', 'phone']
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal Information', {'fields': ('email', 'phone', 'birth_date')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important Dates', {'fields': ('last_login', 'date_joined')}),
    )

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(UserActivity)