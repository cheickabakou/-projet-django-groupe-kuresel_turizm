from django.urls import path
from . import views

app_name = 'visite'

urlpatterns = [
    path('', views.index, name='index'),
    path('destinations/', views.destinations, name='destinations'),
    path('booking/', views.booking, name='booking'),  # Changé
    path('confirmation/<int:reservation_id>/', views.confirmation, name='confirmation'),
    path('booking/<int:reservation_id>/delete/', views.delete_booking, name='delete_booking'),  # Changé
    path('my_bookings/', views.my_bookings, name='my_bookings'),  # Changé
    path('booking/<int:reservation_id>/ticket/', views.ticket_pdf, name='ticket_pdf'),
]