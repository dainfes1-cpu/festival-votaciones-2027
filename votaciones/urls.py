from django.urls import path
from . import views

urlpatterns = [
    # Rutas de la Entrega 2
    path('', views.inicio, name='inicio'),
    path('login/', views.MiLoginView.as_view(), name='login'),
    path('logout/', views.MiLogoutView.as_view(), name='logout'),
    path('registro/', views.registro, name='registro'),
    
    # Rutas de la Entrega 3 (Votaciones)
    path('categorias/', views.lista_categorias, name='lista_categorias'),
    path('categorias/<int:categoria_id>/', views.ver_opciones, name='ver_opciones'),
    path('votar/', views.registrar_voto, name='registrar_voto'),
    
    # NUEVAS RUTAS (Si Oscar usó las vistas 'votaciones' y 'opciones')
    path('votaciones/<int:categoriaId>/', views.votaciones, name='votaciones'),
    path('votacion/<int:votacionId>/', views.votacionSolicitada, name='votacion_solicitada'),
    path('opciones/<int:votacionId>/', views.opciones, name='opciones'),
    
    # API (Descomentada)
    path('api/categorias/', views.api_categorias, name='api_categorias'),
]