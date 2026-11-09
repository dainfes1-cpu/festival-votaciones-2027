from django.urls import path
from . import views

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('login/', views.MiLoginView.as_view(), name='login'),
    path('logout/', views.MiLogoutView.as_view(), name='logout'),
    path('registro/', views.registro, name='registro'),
    path('categorias/', views.lista_categorias, name='categorias'),
    path('votar/', views.registrar_voto, name='registrar_voto'),
    path('votaciones/<int:categoriaId>/', views.votaciones, name='votaciones'),
    path('votacion/<int:votacionId>/', views.votacionSolicitada, name='votacion'),
    path('opciones/<int:votacionId>/', views.opciones, name='opciones'),
]