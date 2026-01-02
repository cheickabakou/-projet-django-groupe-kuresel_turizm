from django.contrib import admin
from .models import Destination, Reservation

@admin.register(Destination)
class DestinationAdmin(admin.ModelAdmin):
    list_display = ("nom", "price", "discount", "available", "duration")
    list_filter = ("available",)
    search_fields = ("nom",)
    list_editable = ("price", "discount", "available")
    
@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = (
        "nom_client",
        "destination",
        "nb_personnes",
        "total_price",
        "created_at",
        "telephone"
    )
    list_filter = ("destination", "created_at")
    search_fields = ("nom_client", "email", "telephone")
    ordering = ("-created_at",)
    