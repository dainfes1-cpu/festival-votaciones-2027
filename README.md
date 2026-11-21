# Sistema Web de Votaciones – Festival de la Leyenda Vallenata

Este proyecto es la primera versión funcional del Sistema Web de Votaciones de la Fundación Festival de la Leyenda Vallenata, desarrollada para el Eje 2 de la asignatura Desarrollo Web de Areandina. Fue construido por un equipo de cuatro integrantes: Yudy Andrea Galeano Mendoza, David Infante Escobar y Oscar Danilo Chala Villegas.

El sistema está hecho con Django, siguiendo el patrón MVT (modelo, vista y plantilla), y usa MySQL como base de datos. En esta entrega los usuarios pueden registrarse, iniciar sesión y cerrar sesión. Los administradores pueden crear ediciones del festival, categorías, votaciones y opciones desde el panel de administración de Django, y la página de inicio muestra al público las votaciones guardadas en la base de datos. Cada elemento depende del anterior: una edición tiene categorías, cada categoría tiene votaciones y cada votación tiene opciones.

El código está en dos carpetas. La carpeta config contiene la configuración general del proyecto, y la carpeta votaciones contiene la aplicación principal con los modelos, las vistas, las rutas, el formulario de registro, las plantillas HTML, las migraciones y las pruebas.

Para ejecutarlo hace falta tener instalados Python 3.10 o superior, Git y MySQL. Primero se clona el repositorio con git clone https://github.com/dainfes1-cpu/festival-votaciones-2027.git y se entra a la carpeta del proyecto. Luego se crea un entorno virtual con python -m venv .venv y se activa con .venv\Scripts\activate en Windows, o con source .venv/bin/activate en Mac y Linux. Con el entorno activado se instalan las dependencias con pip install -r requirements.txt, o, si ese archivo no existe, con pip install django mysqlclient.

## Registro seguro de votos
El sistema permite registrar votos únicamente a usuarios autenticados que seleccionen una opción válida.
Antes de registrar un voto, la aplicación verifica:
- Que la edición esté activa.
- Que la votación esté abierta y dentro de su período establecido.
- Que la opción pertenezca a la votación.
- Que el usuario no haya votado anteriormente en la misma categoría y edición.

Se utiliza una transacción para garantizar la integridad del registro y una restricción única en el modelo `Voto` para evitar votos duplicados, incluso cuando existan solicitudes simultáneas.
Las pruebas relacionadas verifican el registro exitoso, los votos duplicados, las votaciones cerradas o todavía no iniciadas, las ediciones cerradas y el envío sin opción seleccionada.

## Pruebas automáticas
Las pruebas se ejecutan con:
```bash
python manage.py test votaciones -v 2
python manage.py makemigrations --check --dry-run

## Informacion importante 
El proyecto usa una base de datos de prueba llamada db_festival, ya creada en MySQL y configurada en el archivo config/settings.py, donde solo hay que revisar que el usuario y la contraseña de MySQL correspondan a los del computador donde se ejecuta el proyecto. Para el cliente, esa base de datos no se entrega con información cargada: el usuario administrador es quien la va llenando a medida que el festival lo necesita, creando las ediciones, categorías, votaciones y opciones, mientras que los demás usuarios se registran por sí mismos desde el sitio. Para empezar se aplican las migraciones con python manage.py migrate, se crea el usuario administrador con python manage.py createsuperuser y se inicia el servidor con python manage.py runserver. El sitio público queda disponible en http://127.0.0.1:8000/ y el panel de administración en http://127.0.0.1:8000/admin/.

Para tener datos de prueba iniciales, se entra al panel de administración con el usuario creado y se registra, en este orden, una edición (por ejemplo 2027), una categoría de esa edición, una votación con sus fechas de inicio y fin, y varias opciones para esa votación. Al volver a la página de inicio, la votación aparece en la lista.
Las pruebas automáticas están en el archivo votaciones/tests.py y se ejecutan con python manage.py test votaciones -v 2. Django crea una base de datos temporal para ellas y la elimina al terminar, por lo que el usuario de MySQL debe tener permiso para crear bases de datos.
