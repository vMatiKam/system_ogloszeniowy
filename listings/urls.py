from django.urls import path
from . import views

urlpatterns = [
    # Wyszukiwarka & Główna
    path('', views.listing_list, name='listing_list'),
    path('listing/add/', views.listing_create, name='listing_create'),
    path('listing/<slug:slug>/', views.listing_detail, name='listing_detail'),
    
    # Moje ogłoszenia (Zarządzanie)
    path('my-listings/', views.my_listings, name='my_listings'),
    path('listing/<slug:slug>/edit/', views.listing_edit, name='listing_edit'),
    path('listing/<slug:slug>/delete/', views.listing_delete, name='listing_delete'),
    path('listing/<slug:slug>/toggle-status/', views.toggle_status, name='toggle_status'),
    
    # Ulubione
    path('my-favorites/', views.my_favorites, name='my_favorites'),
    path('listing/<slug:slug>/favorite/', views.toggle_favorite, name='toggle_favorite'),
    
    # Wiadomości
    path('listing/<slug:listing_slug>/contact/', views.send_message, name='send_message'),
    path('inbox/', views.inbox_view, name='inbox'),
]