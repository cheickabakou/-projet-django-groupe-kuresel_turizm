from django.urls import path
from . import views

app_name = 'visite'

urlpatterns = [
    path('', views.index, name='index'),
    path('destinations/', views.destinations, name='destinations'),
    path('reservation/', views.reservation, name='reservation'),
]