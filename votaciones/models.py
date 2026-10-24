from django.db import models

class Edicion(models.Model):
    anio = models.IntegerField(unique=True, help_text="Año de la edición del festival")
    activa = models.BooleanField(default=False, help_text="Indica si es la edición actual")

    class Meta:
        verbose_name_plural = "Ediciones"
        ordering = ['-anio'] # Para que salgan de la más reciente a la más antigua

    def __str__(self):
        return f"Edición {self.anio}"

class Categoria(models.Model):
    nombre = models.CharField(max_length=100)
    edicion = models.ForeignKey(Edicion, on_delete=models.CASCADE, related_name='categorias')

    class Meta:
        verbose_name_plural = "Categorías"

    def __str__(self):
        return f"{self.nombre} ({self.edicion.anio})"

class Votacion(models.Model):
    nombre = models.CharField(max_length=150)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, related_name='votaciones')
    fecha_inicio = models.DateTimeField()
    fecha_fin = models.DateTimeField()

    class Meta:
        verbose_name_plural = "Votaciones"

    def __str__(self):
        return self.nombre

class Opcion(models.Model):
    nombre = models.CharField(max_length=150)
    votacion = models.ForeignKey(Votacion, on_delete=models.CASCADE, related_name='opciones')

    class Meta:
        verbose_name_plural = "Opciones"

    def __str__(self):
        return self.nombre