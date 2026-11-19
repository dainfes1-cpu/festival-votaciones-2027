from django.urls import path
from . import views

urlpatterns = [
    # Rutas de la Entrega 2
    path('', views.inicio, name='inicio'),
    path('login/', views.MiLoginView.as_view(), name='login'),
    path('logout/', views.MiLogoutView.as_view(), name='logout'),
    path('registro/', views.registro, name='registro'),
    
    # 👇 RUTA MODIFICADA: Le agregamos 'votaciones/' al inicio para que no choque
    path('votaciones/categorias/<int:votacion_id>/', views.lista_categorias, name='lista_categorias_votacion'),
    
    # Rutas de categorías y votación
    path('categorias/', views.lista_categorias, name='lista_categorias'),
    path('categorias/<int:categoria_id>/', views.ver_opciones, name='ver_opciones'),
    path('votar/', views.registrar_voto, name='registrar_voto'),
    
    # Rutas auxiliares
    path('votaciones/<int:categoriaId>/', views.votaciones, name='votaciones'),
    path('votacion/<int:votacionId>/', views.votacionSolicitada, name='votacion_solicitada'),
    path('opciones/<int:votacionId>/', views.opciones, name='opciones'),
    
    # Dashboard y API
    path('resultados/', views.resultados, name='resultados'),
    path('api/categorias/', views.api_categorias, name='api_categorias'),
]