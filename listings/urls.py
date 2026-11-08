from django.urls import path
from . import views

urlpatterns = [
    path('', views.listing_list, name='listing_list'),
    path('listing/add/', views.listing_create, name='listing_create'),
    path('listing/<slug:slug>/', views.listing_detail, name='listing_detail'),
]