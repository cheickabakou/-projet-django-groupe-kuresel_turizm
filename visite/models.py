from django.db import models
from django.utils import timezone

class Destination(models.Model):
    nom = models.CharField("Destination Name", max_length=100)
    description = models.TextField("Description", blank=True)
    image = models.ImageField("Image", upload_to="destinations/")
    price = models.DecimalField("Price (€)", max_digits=8, decimal_places=2)
    discount = models.PositiveIntegerField("Discount (%)", default=0)
    duration = models.CharField("Duration", max_length=50)
    available = models.BooleanField("Available", default=True)

    def final_price(self):
        if self.discount > 0:
            return self.price - (self.price * self.discount / 100)
        return self.price

    def __str__(self):
        return self.nom

    class Meta:
        verbose_name = "Destination"
        verbose_name_plural = "Destinations"


class Reservation(models.Model):
    destination = models.ForeignKey(
        Destination,
        verbose_name="Destination",
        on_delete=models.CASCADE,
        related_name="reservations"
    )
    nom_client = models.CharField("Customer Name", max_length=100)
    email = models.EmailField("Email")
    telephone = models.CharField("Phone", max_length=20)
    nb_personnes = models.PositiveIntegerField("Number of People")
    total_price = models.DecimalField("Total Price (€)", max_digits=10, decimal_places=2, default=0.00)
    created_at = models.DateTimeField("Booking Date", auto_now_add=True)

    def __str__(self):
        return f"{self.nom_client} - {self.destination.nom}"
    
    def formatted_date(self):
        return self.created_at.strftime("%d/%m/%Y %H:%M")
    formatted_date.short_description = "Booking Date"
    
    def day_only(self):
        return self.created_at.strftime("%d/%m/%Y")
    day_only.short_description = "Day"

    class Meta:
        verbose_name = "Reservation"
        verbose_name_plural = "Reservations"