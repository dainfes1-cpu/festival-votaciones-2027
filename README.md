# Sistema Web de Votaciones – Festival de la Leyenda Vallenata

Este proyecto es la primera versión funcional del Sistema Web de Votaciones de la Fundación Festival de la Leyenda Vallenata, desarrollada para el Eje 2 de la asignatura Desarrollo Web de Areandina.

## Integrantes

Equipo de tres integrantes:

- Yudy Andrea Galeano Mendoza
- David Infante Escobar
- Oscar Danilo Chala Villegas

## Descripción

El sistema está hecho con Django, siguiendo el patrón MVT, y usa MySQL como base de datos.

En esta entrega:

- Los usuarios pueden registrarse, iniciar sesión y cerrar sesión.
- Los administradores pueden crear ediciones del festival, categorías, votaciones y opciones desde el panel de administración de Django.
- La página de inicio muestra al público las votaciones guardadas en la base de datos.

Cada elemento depende del anterior: una edición tiene categorías, cada categoría tiene votaciones y cada votación tiene opciones.

## Estructura del proyecto

- `config/`: configuración general del proyecto.
- `votaciones/`: aplicación principal con los modelos, las vistas, las rutas, el formulario de registro, las plantillas HTML, las migraciones y las pruebas.

## Requisitos

- Python 3.10 o superior
- Git
- MySQL

## Instalación

1. Clonar el repositorio y entrar a la carpeta del proyecto:

```
git clone https://github.com/dainfes1-cpu/festival-votaciones-2027.git
cd festival-votaciones-2027
```

2. Crear el entorno virtual:

```
python -m venv .venv
```

3. Activarlo. En Windows:

```
.venv\Scripts\activate
```

En Mac y Linux:

```
source .venv/bin/activate
```

4. Instalar las dependencias:

```
pip install -r requirements.txt
```

Si ese archivo no existe, usar:

```
pip install django mysqlclient
```

Si `mysqlclient` da error en Windows, se puede probar con `pip install pymysql`.

## Base de datos

En esta etapa el proyecto usa una base de datos de prueba llamada `db_festival`, ya creada en MySQL y configurada en `config/settings.py`. Solo hay que revisar que el usuario y la contraseña de MySQL correspondan a los del computador donde se ejecuta el proyecto.

Para el cliente, la base de datos no se entrega con información cargada: el usuario administrador la va llenando a medida que el festival lo necesita, creando las ediciones, categorías, votaciones y opciones, mientras que los demás usuarios se registran por sí mismos desde el sitio.

## Ejecución

Aplicar las migraciones, crear el usuario administrador e iniciar el servidor:

```
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

- Sitio público: http://127.0.0.1:8000/
- Panel de administración: http://127.0.0.1:8000/admin/

## Datos de prueba

Para tener datos de prueba, entrar al panel de administración con el usuario creado y registrar, en este orden:

1. Una edición (por ejemplo 2027).
2. Una categoría de esa edición.
3. Una votación con sus fechas de inicio y fin.
4. Varias opciones para esa votación.

Al volver a la página de inicio, la votación aparece en la lista.

## Pruebas

Las pruebas automáticas están en `votaciones/tests.py` y se ejecutan con:

```
python manage.py test votaciones -v 2
```

Django crea una base de datos temporal para ellas y la elimina al terminar, por lo que el usuario de MySQL debe tener permiso para crear bases de datos.
