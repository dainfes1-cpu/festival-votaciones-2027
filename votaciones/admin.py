from django.contrib import admin
from .models import Edicion, Categoria, Votacion, Opcion, Voto

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

# ESTA ES LA NUEVA PARTE PARA LA ENTREGA 3
@admin.register(Voto)
class VotoAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'categoria', 'opcion', 'fecha_voto')
    # Opcional: para que puedas filtrar y ver mejor los votos en el admin
    list_filter = ('categoria', 'edicion')