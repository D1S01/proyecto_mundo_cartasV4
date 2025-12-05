from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout
from django.contrib import messages
from .forms import CustomUserCreationForm
from usuarios.models import Usuario

# Create your views here.
def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            messages.success(request, f"Bienvenid@ {form.get_user().username}")
            user = form.get_user()
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "Error: usuario o contraseña incorrectos")
    form = AuthenticationForm()
    return render(request, 'registration/login.html', {'form':form})

def registrar(request):
    form = CustomUserCreationForm(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            form.save()
            messages.success(request, "cuenta creada")
            return redirect('login')
        messages.error(request, "error al crear la cuenta")
    return render(request, 'registration/registrar.html', {'form':form})
    

def logout_view(request):
    logout(request)
    return redirect('login')