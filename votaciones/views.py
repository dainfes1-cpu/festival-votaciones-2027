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