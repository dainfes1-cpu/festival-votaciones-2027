from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from votaciones.models import Edicion, Categoria, Votacion, Opcion, Voto
from django.utils import timezone
from datetime import timedelta

class Command(BaseCommand):
    help = 'Carga datos de prueba masivos para el Festival Vallenato'

    def handle(self, *args, **kwargs):
        self.stdout.write("Iniciando carga masiva de datos...")

        # 1. Crear Usuarios
        usuarios = []
        for i in range(1, 4):
            username = f'votante{i}'
            if not User.objects.filter(username=username).exists():
                user = User.objects.create_user(username=username, password='123456')
                usuarios.append(user)
        self.stdout.write("Usuarios creados (votante1, votante2, votante3 - pass: 123456)")

        # 2. Crear Ediciones
        edicion_2026, _ = Edicion.objects.get_or_create(anio=2026, defaults={'activa': False})
        edicion_2027, _ = Edicion.objects.get_or_create(anio=2027, defaults={'activa': True})
        self.stdout.write("Ediciones creadas (2026, 2027)")

        # 3. Crear Categorías, Votaciones y Opciones para 2027
        categorias_data = [
            {"nombre": "Acordeonero Profesional", "opciones": ["Almes Granados", "Carlos Vives", "Juancho Rois"]},
            {"nombre": "Canción Inédita", "opciones": ["La Vallenata", "Mi Tierra", "El Río"]},
            {"nombre": "Piloneras", "opciones": ["Grupo A", "Grupo B", "Grupo C"]},
            {"nombre": "Mejor Vestuario", "opciones": ["Diseño 1", "Diseño 2"]}
        ]

        ahora = timezone.now()

        for cat_data in categorias_data:
            cat, _ = Categoria.objects.get_or_create(nombre=cat_data["nombre"], edicion=edicion_2027)
            
            # Crear votación asociada a la categoría
            votacion, _ = Votacion.objects.get_or_create(
                nombre=f"Voto popular - {cat.nombre}",
                categoria=cat,
                defaults={
                    'fecha_inicio': ahora - timedelta(days=1),
                    'fecha_fin': ahora + timedelta(days=10)
                }
            )

            # Crear opciones (participantes) y simular votos
            for idx, opcion_nombre in enumerate(cat_data["opciones"]):
                opcion, _ = Opcion.objects.get_or_create(nombre=opcion_nombre, votacion=votacion)
                
                # Simular votos (solo votamos con el votante1 en la primera opción para no romper la regla unique_together)
                if idx == 0 and usuarios:
                    try:
                        Voto.objects.create(
                            usuario=usuarios[0],
                            edicion=edicion_2027,
                            categoria=cat,
                            opcion=opcion
                        )
                    except Exception:
                        pass # Ignorar si el voto ya existe

        self.stdout.write(self.style.SUCCESS("¡Carga masiva completada con éxito!"))
        self.stdout.write("Puedes entrar al Admin y ver los datos creados.")