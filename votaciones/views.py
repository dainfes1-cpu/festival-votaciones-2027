from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from .models import Edicion, Categoria, Votacion, Opcion
from .forms import RegistroForm

# 1. Vista de la página de inicio
def inicio(request):
    ediciones = Edicion.objects.all()
    categorias = Categoria.objects.all()
    votaciones = Votacion.objects.all()
    opciones = Opcion.objects.all()
    
    contexto = {
        'ediciones': ediciones,
        'categorias': categorias,
        'votaciones': votaciones,
        'opciones': opciones,
    }
    return render(request, 'inicio.html', contexto)

# 2. Vista de Registro
def registro(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user) 
            return redirect('inicio')
    else:
        form = RegistroForm()
    return render(request, 'registro.html', {'form': form})

# 3. Vistas de Login y Logout
class MiLoginView(LoginView):
    template_name = 'login.html'
    redirect_authenticated_user = True

class MiLogoutView(LogoutView):
    next_page = reverse_lazy('login')

# 4. Vista de Categorias
def categorias(request, anio):
    categorias = Categoria.objects.filter(
        edicion__anio=anio
    )
    votaciones = Votacion.objects.filter(
        categoria__edicion__anio=anio
    )
    print(votaciones, 'aksjdhgaskjdh')
    contexto = {
            'anio': anio,
            'categorias': categorias,
            'votaciones' : votaciones
        }
    return render(request, 'categorias.html', contexto)

# 5. Vista de Votaciones
def votaciones(request, categoriaId):
    votaciones = Votacion.objects.filter(
            categoria__id=categoriaId
        )
    contexto = {
            'votaciones' : votaciones
        }
    return render(request, 'votaciones.html', contexto)

# 5. Vista de Votacion seleccionada
def votacionSolicitada(request, votacionId):
    votacion = Votacion.objects.filter(
            id=votacionId
        ).first()
    contexto = {
            'votacion' : votacion
        }
    return render(request, 'votacion.html', contexto)

# 5. Vista de opciones a votar
def opciones(request, votacionId):
    opciones = Opcion.objects.filter(
            votacion_id=votacionId
        )
    contexto = {
            'opciones' : opciones
        }
    return render(request, 'opciones.html', contexto)