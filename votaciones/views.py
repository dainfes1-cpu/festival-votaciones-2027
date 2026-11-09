from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse_lazy
from .models import Edicion, Categoria, Votacion, Opcion, Voto
from .forms import RegistroForm

# --- VISTAS DE LA ENTREGA 2 ---

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

class MiLoginView(LoginView):
    template_name = 'login.html'
    redirect_authenticated_user = True

class MiLogoutView(LogoutView):
    next_page = reverse_lazy('login')

# --- VISTAS DE LA ENTREGA 3 (VOTACIONES) ---

def lista_categorias(request):
    edicion_activa = Edicion.objects.filter(activa=True).first()
    categorias = Categoria.objects.filter(edicion=edicion_activa) if edicion_activa else []
    votaciones = Votacion.objects.filter(
        categoria__edicion__anio=edicion_activa.anio
    )
    categorias_votadas = []
    if request.user.is_authenticated:
        categorias_votadas = Voto.objects.filter(usuario=request.user, edicion=edicion_activa).values_list('categoria_id', flat=True)

    return render(request, 'categorias.html', {
        'anio': edicion_activa.anio,
        'categorias': categorias,
        'categorias_votadas': categorias_votadas,
        'votaciones': votaciones,
    })

@login_required
def ver_opciones(request, categoria_id):
    categoria = get_object_or_404(Categoria, id=categoria_id)
    
    if Voto.objects.filter(usuario=request.user, categoria=categoria).exists():
        messages.error(request, "Ya has emitido tu voto en esta categoría.")
        return redirect('lista_categorias')
    
    opciones = Opcion.objects.filter(votacion__categoria=categoria)
    return render(request, 'opciones.html', {'categoria': categoria, 'opciones': opciones})

@login_required
def registrar_voto(request):
    if request.method == 'POST':
        opcion_id = request.POST.get('opcion_id')
        opcion = get_object_or_404(Opcion, id=opcion_id)
        categoria = opcion.votacion.categoria
        edicion = categoria.edicion

        if Voto.objects.filter(usuario=request.user, categoria=categoria, edicion=edicion).exists():
            messages.error(request, "Error: Ya has votado en esta categoría.")
            return redirect('lista_categorias')

        Voto.objects.create(
            usuario=request.user,
            categoria=categoria,
            edicion=edicion,
            opcion=opcion
        )
        messages.success(request, f"¡Voto registrado por {opcion.nombre}!")
        return redirect('lista_categorias')
    
    return redirect('lista_categorias')

# 5. Vista de Votaciones
def votaciones(request, categoriaId):
    votaciones = Votacion.objects.filter(
            categoria__id=categoriaId
        )
    contexto = {
            'votaciones' : votaciones
        }
    return render(request, 'votaciones.html', contexto)

# 6. Vista de Votacion seleccionada
def votacionSolicitada(request, votacionId):
    votacion = Votacion.objects.filter(
            id=votacionId
        ).first()
    contexto = {
            'votacion' : votacion
        }
    return render(request, 'votacion.html', contexto)

# 7. Vista de opciones a votar
@login_required
def opciones(request, votacionId):
    opciones = Opcion.objects.filter(
            votacion_id=votacionId
        )
    contexto = {
            'opciones' : opciones
        }
    return render(request, 'opciones.html', contexto)