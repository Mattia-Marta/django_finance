from django.urls import path
from . import views

app_name = 'spesa'  # Importante per il namespacing degli URL

urlpatterns = [
    path('', views.lista_spese, name='lista_spese'),  # Lista di tutte le spese
    path('nuova/', views.nuova_spesa, name='nuova_spesa'),  # Form per creare una nuova spesa
    path('modifica/<int:pk>/', views.modifica_spesa, name='modifica_spesa'),  # Form per modificare una spesa esistente
    path('elimina/<int:pk>/', views.elimina_spesa, name='elimina_spesa'), # Vista per eliminare una spesa

    
    path('webhook/', views.telegram_webhook, name='telegram_webhook'),
    path('set_webhook/', views.set_webhook, name='set_webhook'),
]