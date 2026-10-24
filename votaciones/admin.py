from django.contrib import admin
from .models import Edicion, Categoria, Votacion, Opcion

@admin.register(Edicion)
class EdicionAdmin(admin.ModelAdmin):
    list_display = ('anio', 'activa')

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'edicion')

@admin.register(Votacion)
class VotacionAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'categoria', 'fecha_inicio', 'fecha_fin')

@admin.register(Opcion)
class OpcionAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'votacion')