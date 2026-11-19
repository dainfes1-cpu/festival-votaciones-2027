from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse_lazy
from django.db.models import Count
from django.contrib.admin.views.decorators import staff_member_required
from django.utils import timezone
from django.http import JsonResponse
from django.db import IntegrityError

from .models import Edicion, Categoria, Votacion, Opcion, Voto
from .forms import RegistroForm

# --- VISTAS DE LA ENTREGA 2 (BASE) ---

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


# --- VISTAS DE LA ENTREGA 3 Y 4 (VOTACIONES Y RESULTADOS) ---

def lista_categorias(request):
    edicion_activa = Edicion.objects.filter(activa=True).first()
    categorias = []
    categorias_votadas = []

    if edicion_activa:
        categorias = Categoria.objects.filter(edicion=edicion_activa).distinct()
        
        if request.user.is_authenticated:
            categorias_votadas = Voto.objects.filter(
                usuario=request.user, 
                edicion=edicion_activa
            ).values_list('categoria_id', flat=True)

    return render(request, 'categorias.html', {
        'edicion': edicion_activa,
        'categorias': categorias,
        'categorias_votadas': categorias_votadas
    })

@login_required
def ver_opciones(request, categoria_id):
    categoria = get_object_or_404(Categoria, id=categoria_id)
    
    # Validar si ya votó en esta categoría
    if Voto.objects.filter(usuario=request.user, categoria=categoria).exists():
        messages.error(request, "Ya has emitido tu voto en esta categoría.")
        return redirect('lista_categorias')
    
    opciones = Opcion.objects.filter(votacion__categoria=categoria)
    return render(request, 'opciones.html', {'categoria': categoria, 'opciones': opciones})

@login_required
def registrar_voto(request):
    if request.method == 'POST':
        opcion_id = request.POST.get('opcion_id')
        
        if not opcion_id:
            messages.error(request, "Debes seleccionar una opción.")
            return redirect('lista_categorias')

        opcion = get_object_or_404(Opcion, id=opcion_id)
        votacion = opcion.votacion
        categoria = votacion.categoria
        edicion = categoria.edicion
        ahora = timezone.now()

        # 1. Validar que la edición esté activa
        if not edicion.activa:
            messages.error(request, "Esta edición está cerrada. No se permiten votos.")
            return redirect('lista_categorias')

        # 2. Validar que estemos dentro del rango de fechas de la votación
        if not (votacion.fecha_inicio <= ahora <= votacion.fecha_fin):
            messages.error(request, "La votación está cerrada o no ha comenzado.")
            return redirect('lista_categorias')

        # 3. Validar duplicados antes de intentar guardar
        if Voto.objects.filter(usuario=request.user, categoria=categoria, edicion=edicion).exists():
            messages.error(request, "Error: Ya has votado en esta categoría.")
            return redirect('lista_categorias')

        # 4. Registrar el voto con manejo de errores de integridad
        try:
            Voto.objects.create(
                usuario=request.user,
                categoria=categoria,
                edicion=edicion,
                opcion=opcion
            )
            messages.success(request, f"¡Voto registrado por {opcion.nombre}!")
        except IntegrityError:
            # Esto captura si dos peticiones idénticas llegan al mismo tiempo (concurrencia)
            messages.error(request, "Error de integridad: Tu voto ya fue registrado.")
            
        return redirect('lista_categorias')
    
    return redirect('lista_categorias')

# --- VISTA DE RESULTADOS CON DATOS PARA GRÁFICOS (SOLO ADMIN) ---

@staff_member_required
def resultados(request):
    edicion_activa = Edicion.objects.filter(activa=True).first()
    
    if not edicion_activa:
        return render(request, 'resultados.html', {'resultados': [], 'edicion': None})

    # 1. Resultados agrupados por opción (para las tarjetas y el gráfico de barras)
    resultados_data = Opcion.objects.filter(
        votacion__categoria__edicion=edicion_activa
    ).annotate(total_votos=Count('voto')).order_by('-total_votos')

    # 2. Datos para el gráfico circular (votos por categoría)
    votos_por_categoria = Categoria.objects.filter(
        edicion=edicion_activa
    ).annotate(total=Count('voto')).order_by('-total')

    # 3. Preparar listas para pasar a JavaScript (Chart.js)
    nombres_opciones = [op.nombre for op in resultados_data]
    votos_opciones = [op.total_votos for op in resultados_data]
    
    nombres_categorias = [cat.nombre for cat in votos_por_categoria]
    votos_categorias = [cat.total for cat in votos_por_categoria]

    contexto = {
        'resultados': resultados_data,
        'edicion': edicion_activa,
        'nombres_opciones': nombres_opciones,
        'votos_opciones': votos_opciones,
        'nombres_categorias': nombres_categorias,
        'votos_categorias': votos_categorias,
    }

    return render(request, 'resultados.html', contexto)

# --- VISTAS AUXILIARES Y API ---

def votaciones(request, categoriaId):
    votaciones = Votacion.objects.filter(categoria__id=categoriaId)
    return render(request, 'votaciones.html', {'votaciones': votaciones})

def votacionSolicitada(request, votacionId):
    votacion = Votacion.objects.filter(id=votacionId).first()
    return render(request, 'votacion.html', {'votacion': votacion})

@login_required
def opciones(request, votacionId):
    opciones = Opcion.objects.filter(votacion_id=votacionId)
    return render(request, 'opciones.html', {'opciones': opciones})

def api_categorias(request):
    edicion_activa = Edicion.objects.filter(activa=True).first()
    categorias = Categoria.objects.filter(edicion=edicion_activa)
    
    data = []
    for cat in categorias:
        opciones = Opcion.objects.filter(votacion__categoria=cat)
        data.append({
            'id': cat.id,
            'nombre': cat.nombre,
            'opciones': [{'id': op.id, 'nombre': op.nombre} for op in opciones]
        })
    
    return JsonResponse({'categorias': data})