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
from django.db import IntegrityError, transaction
from .models import Edicion, Categoria, Votacion, Opcion, Voto
from .forms import RegistroForm

# --- VISTAS DE LA ENTREGA 2 (BASE) ---

def inicio(request):
    ahora = timezone.now()
    ediciones = Edicion.objects.all()
    categorias = Categoria.objects.all()
    
    # Solo mostramos votaciones que estén activas en fechas
    votaciones = Votacion.objects.filter(
        fecha_inicio__lte=ahora, 
        fecha_fin__gte=ahora
    )
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

def lista_categorias(request, votacion_id=None):
    edicion_activa = Edicion.objects.filter(activa=True).first()
    categorias = []
    categorias_votadas = []
    votacion_actual = None

    if edicion_activa:
        if votacion_id:
            # Filtramos las categorías que pertenecen a la votación seleccionada
            votacion_actual = get_object_or_404(Votacion, id=votacion_id)
            categorias = Categoria.objects.filter(edicion=edicion_activa, votaciones=votacion_actual).distinct()
        else:
            # Si no viene votación, mostramos todas
            categorias = Categoria.objects.filter(edicion=edicion_activa).distinct()
        
        if request.user.is_authenticated:
            categorias_votadas = Voto.objects.filter(
                usuario=request.user, 
                edicion=edicion_activa
            ).values_list('categoria_id', flat=True)

    return render(request, 'categorias.html', {
        'edicion': edicion_activa,
        'categorias': categorias,
        'categorias_votadas': categorias_votadas,
        'votacion_actual': votacion_actual
    })

@login_required
def ver_opciones(request, categoria_id):
    categoria = get_object_or_404(Categoria, id=categoria_id)
    ahora = timezone.now()
    
    # Validar que la votación esté abierta antes de mostrar opciones
    votacion = Votacion.objects.filter(categoria=categoria).first()
    if votacion and not (votacion.fecha_inicio <= ahora <= votacion.fecha_fin):
        messages.error(request, "Esta votación ya se encuentra cerrada.")
        return redirect('lista_categorias')

    # Validar si ya votó en esta categoría
    if Voto.objects.filter(usuario=request.user, categoria=categoria).exists():
        messages.error(request, "Ya has emitido tu voto en esta categoría.")
        return redirect('lista_categorias')
    
    opciones = Opcion.objects.filter(votacion__categoria=categoria)
    return render(request, 'opciones.html', {'categoria': categoria, 'opciones': opciones})

@login_required
def registrar_voto(request):
    # Esta vista solo registra votos enviados mediante POST.
    if request.method != "POST":
        return redirect("lista_categorias")

    # Comprobamos que se haya seleccionado una opción.
    opcion_id = request.POST.get("opcion_id")
    if not opcion_id:
        messages.error(request, "Debes seleccionar una opción.")
        return redirect("lista_categorias")

    # Buscamos la opción; si no existe, Django responde con 404.
    opcion = get_object_or_404(Opcion, pk=opcion_id)

    # Obtenemos la votación, categoría y edición relacionadas con la opción.
    votacion = opcion.votacion
    categoria = votacion.categoria
    edicion = categoria.edicion
    ahora = timezone.now()

    # No se puede votar en una edición que está cerrada.
    if not edicion.activa:
        messages.error(
            request,
            "Esta edición está cerrada. No se permiten votos."
        )
        return redirect("lista_categorias")

    # La fecha actual debe estar entre el inicio y el cierre de la votación.
    if not (votacion.fecha_inicio <= ahora <= votacion.fecha_fin):
        messages.error(
            request,
            "La votación está cerrada o todavía no ha comenzado."
        )
        return redirect("lista_categorias")

    # Esta comprobación da una respuesta clara en los duplicados normales.
    ya_voto = Voto.objects.filter(
        usuario=request.user,
        categoria=categoria,
        edicion=edicion,
    ).exists()

    if ya_voto:
        messages.error(request, "Ya has votado en esta categoría.")
        return redirect("lista_categorias")

    try:
        # La transacción agrupa el intento de registro del voto.
        with transaction.atomic():
            Voto.objects.create(
                usuario=request.user,
                categoria=categoria,
                edicion=edicion,
                opcion=opcion,
            )

    except IntegrityError:
        # La restricción única de la base de datos protege contra
        # dos solicitudes simultáneas del mismo usuario.
        messages.error(request, "Ya has votado en esta categoría.")
    else:
        messages.success(
            request,
            f"¡Voto registrado por {opcion.nombre}!"
        )

    return redirect("lista_categorias")

# --- VISTA DE RESULTADOS CON TARJETAS RESUMEN Y GRÁFICOS ---

@staff_member_required
def resultados(request):
    edicion_activa = Edicion.objects.filter(activa=True).first()
    
    if not edicion_activa:
        return render(request, 'resultados.html', {'resultados': [], 'edicion': None})

    # 1. Datos para las tarjetas de resumen
    total_votos = Voto.objects.filter(edicion=edicion_activa).count()
    total_categorias = Categoria.objects.filter(edicion=edicion_activa).count()
    total_participantes = Opcion.objects.filter(votacion__categoria__edicion=edicion_activa).count()

    # 2. Resultados agrupados por opción (Tarjetas y Gráfico de Barras)
    resultados_data = Opcion.objects.filter(
        votacion__categoria__edicion=edicion_activa
    ).annotate(total_votos=Count('voto')).order_by('-total_votos')

    # 3. Datos para el gráfico circular (Votos por categoría)
    votos_por_categoria = Categoria.objects.filter(
        edicion=edicion_activa
    ).annotate(total=Count('voto')).order_by('-total')

    # 4. Preparar listas para Chart.js
    nombres_opciones = [op.nombre for op in resultados_data]
    votos_opciones = [op.total_votos for op in resultados_data]
    
    nombres_categorias = [cat.nombre for cat in votos_por_categoria]
    votos_categorias = [cat.total for cat in votos_por_categoria]

    contexto = {
        'resultados': resultados_data,
        'edicion': edicion_activa,
        'total_votos': total_votos,
        'total_categorias': total_categorias,
        'total_participantes': total_participantes,
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