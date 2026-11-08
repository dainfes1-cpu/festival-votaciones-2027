from django.urls import path
from . import views

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('login/', views.MiLoginView.as_view(), name='login'),
    path('logout/', views.MiLogoutView.as_view(), name='logout'),
    path('registro/', views.registro, name='registro'),
    path('categorias/', views.lista_categorias, name='lista_categorias'),
    path('categorias/<int:categoria_id>/', views.ver_opciones, name='ver_opciones'),
    path('votar/', views.registrar_voto, name='registrar_voto'),
]