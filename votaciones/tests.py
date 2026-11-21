from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

from .models import Edicion, Categoria, Votacion, Opcion,Voto


class ModelosTest(TestCase):
    def setUp(self):
        self.edicion = Edicion.objects.create(anio=2027, activa=True)
        self.categoria = Categoria.objects.create(nombre="Acordeonero Profesional", edicion=self.edicion)
        ahora = timezone.now()
        self.votacion = Votacion.objects.create(
            nombre="Favorito del público", categoria=self.categoria,
            fecha_inicio=ahora, fecha_fin=ahora + timedelta(days=7),
        )
        self.opcion = Opcion.objects.create(nombre="Participante 1", votacion=self.votacion)

    def test_relaciones_entre_modelos(self):
        self.assertEqual(self.edicion.categorias.count(), 1)
        self.assertEqual(self.categoria.votaciones.count(), 1)
        self.assertEqual(self.votacion.opciones.count(), 1)

    def test_str_de_edicion(self):
        self.assertEqual(str(self.edicion), "Edición 2027")

    def test_anio_unico(self):
        from django.db import IntegrityError
        with self.assertRaises(IntegrityError):
            Edicion.objects.create(anio=2027)

    def test_borrar_edicion_borra_en_cascada(self):
        self.edicion.delete()
        self.assertEqual(Opcion.objects.count(), 0)


class VistasPublicasTest(TestCase):
    def setUp(self):
        edicion = Edicion.objects.create(anio=2027, activa=True)
        categoria = Categoria.objects.create(nombre="Canción Inédita", edicion=edicion)
        ahora = timezone.now()
        Votacion.objects.create(
            nombre="Votación de prueba", categoria=categoria,
            fecha_inicio=ahora, fecha_fin=ahora + timedelta(days=1),
        )

    def test_inicio_carga_y_muestra_datos_de_la_bd(self):
        r = self.client.get(reverse('inicio'))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "Votación de prueba")

    def test_inicio_vacio_muestra_mensaje(self):
        Votacion.objects.all().delete()
        r = self.client.get(reverse('inicio'))
        self.assertContains(r, "Aún no hay votaciones")


class AutenticacionTest(TestCase):
    def test_paginas_de_login_y_registro_cargan(self):
        self.assertEqual(self.client.get(reverse('login')).status_code, 200)
        self.assertEqual(self.client.get(reverse('registro')).status_code, 200)

    def test_registro_crea_usuario_e_inicia_sesion(self):
        r = self.client.post(reverse('registro'), {
            'username': 'nuevo', 'email': 'nuevo@correo.com',
            'password1': 'ClaveSegura#2027', 'password2': 'ClaveSegura#2027',
        })
        self.assertRedirects(r, reverse('inicio'))
        self.assertTrue(User.objects.filter(username='nuevo').exists())
        self.assertIn('_auth_user_id', self.client.session)

    def test_registro_con_claves_distintas_falla(self):
        self.client.post(reverse('registro'), {
            'username': 'x', 'email': 'x@correo.com',
            'password1': 'ClaveSegura#2027', 'password2': 'otra',
        })
        self.assertFalse(User.objects.filter(username='x').exists())

    def test_login_correcto(self):
        User.objects.create_user('ana', password='ClaveSegura#2027')
        r = self.client.post(reverse('login'), {'username': 'ana', 'password': 'ClaveSegura#2027'})
        self.assertEqual(r.status_code, 302)
        self.assertIn('_auth_user_id', self.client.session)

    def test_login_incorrecto(self):
        User.objects.create_user('ana', password='ClaveSegura#2027')
        r = self.client.post(reverse('login'), {'username': 'ana', 'password': 'mala'})
        self.assertEqual(r.status_code, 200)
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_logout_cierra_sesion(self):
        User.objects.create_user('ana', password='ClaveSegura#2027')
        self.client.login(username='ana', password='ClaveSegura#2027')
        self.client.post(reverse('logout'))
        self.assertNotIn('_auth_user_id', self.client.session)
        
# Create your tests here.
class RegistroVotoTest(TestCase):
    def setUp(self):
        # Preparamos una edición, categoría, votación y opción válidas.
        ahora = timezone.now()

        self.usuario = User.objects.create_user(
            username="votante_prueba",
            password="ClaveSegura#2027",
        )
        self.edicion = Edicion.objects.create(
            anio=2027,
            activa=True,
        )
        self.categoria = Categoria.objects.create(
            nombre="Categoría de prueba",
            edicion=self.edicion,
        )
        self.votacion = Votacion.objects.create(
            nombre="Votación de prueba",
            categoria=self.categoria,
            fecha_inicio=ahora - timedelta(hours=1),
            fecha_fin=ahora + timedelta(hours=1),
        )
        self.opcion = Opcion.objects.create(
            nombre="Opción de prueba",
            votacion=self.votacion,
        )

        # Iniciamos sesión para enviar votos como usuario autenticado.
        self.client.force_login(self.usuario)
        self.url = reverse("registrar_voto")

    def enviar_voto(self):
        # Enviamos el identificador de la opción seleccionada.
        return self.client.post(
            self.url,
            {"opcion_id": self.opcion.pk},
        )

    def test_usuario_puede_registrar_un_voto(self):
        respuesta = self.enviar_voto()

        self.assertEqual(respuesta.status_code, 302)
        self.assertEqual(
            Voto.objects.filter(
                usuario=self.usuario,
                categoria=self.categoria,
                edicion=self.edicion,
            ).count(),
            1,
        )

    def test_usuario_no_puede_votar_dos_veces(self):
        self.enviar_voto()
        respuesta = self.enviar_voto()

        self.assertEqual(respuesta.status_code, 302)
        self.assertEqual(
            Voto.objects.filter(
                usuario=self.usuario,
                categoria=self.categoria,
                edicion=self.edicion,
            ).count(),
            1,
        )

    def test_no_permite_votar_si_la_edicion_esta_cerrada(self):
        self.edicion.activa = False
        self.edicion.save()

        self.enviar_voto()

        self.assertEqual(Voto.objects.count(), 0)

    def test_no_permite_votar_antes_de_que_inicie_la_votacion(self):
        self.votacion.fecha_inicio = timezone.now() + timedelta(days=1)
        self.votacion.save()

        self.enviar_voto()

        self.assertEqual(Voto.objects.count(), 0)

    def test_no_permite_votar_despues_del_cierre(self):
        self.votacion.fecha_fin = timezone.now() - timedelta(days=1)
        self.votacion.save()

        self.enviar_voto()

        self.assertEqual(Voto.objects.count(), 0)

    def test_no_permite_votar_sin_seleccionar_opcion(self):
        respuesta = self.client.post(self.url, {})

        self.assertEqual(respuesta.status_code, 302)
        self.assertEqual(Voto.objects.count(), 0)
