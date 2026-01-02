# account/models.py - COMPLETE AND CORRECT VERSION
from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True, verbose_name="Phone")
    birth_date = models.DateField(null=True, blank=True, verbose_name="Birth Date")
    
    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
    
    def __str__(self):
        return self.username


class UserActivity(models.Model):
    ACTIVITY_TYPES = [
        ('LOGIN', 'Login'),
        ('LOGOUT', 'Logout'),
        ('REGISTER', 'Registration'),
        ('PROFILE_UPDATE', 'Profile Update'),
        ('BOOKING', 'Booking'),
        ('PASSWORD_CHANGE', 'Password Change'),
    ]
    
    user = models.ForeignKey(
        CustomUser, 
        on_delete=models.CASCADE,  
        related_name='activities'
    )
    activity_type = models.CharField(
        max_length=50, 
        choices=ACTIVITY_TYPES,
        default='LOGIN',
        verbose_name="Activity Type"
    )
    timestamp = models.DateTimeField(
        auto_now_add=True,  
        verbose_name="Date and Time"
    )
    ip_address = models.GenericIPAddressField(
        null=True, 
        blank=True,
        verbose_name="IP Address"
    )
    details = models.TextField(
        blank=True,
        verbose_name="Additional Details"
    )
    
    class Meta:
        verbose_name = "User Activity"
        verbose_name_plural = "User Activities"
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.user.username} - {self.get_activity_type_display()} - {self.timestamp}"