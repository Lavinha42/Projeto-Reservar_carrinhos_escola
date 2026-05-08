from django.shortcuts import render, redirect
from .models import Reserva, Equipamento
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login

def home(request):
    return render(request, 'longa.html')
def CriarConta(request):
    if request.method == "POST":
        # Pegando os dados do formulário
        usuario = request.POST.get('usuario')
        email = request.POST.get('email')
        senha = request.POST.get('senha')
        confirmar = request.POST.get('confirmar_senha')

        # 1. Verificar se as senhas batem
        if senha != confirmar:
            messages.error(request, "As senhas não coincidem!")
            return render(request, 'index.html')

        # 2. Verificar se o usuário já existe no banco
        if User.objects.filter(username=usuario).exists():
            messages.error(request, "Este nome de usuário já está em uso.")
            return render(request, 'index.html')

        # 3. Criar o usuário no banco de dados
        user = User.objects.create_user(username=usuario, email=email, password=senha)
        user.save()

        messages.success(request, "Conta criada com sucesso! Faça login.")
        return redirect('longa') # Redireciona para a tela de login

    return render(request, 'index.html')
def Entrar(request):
    if request.method == "POST":
        usuario_digitado = request.POST.get('usuario')
        senha_digitada = request.POST.get('senha')

        # Verifica no banco de dados se o usuário e senha batem
        user = authenticate(request, username=usuario_digitado, password=senha_digitada)

        if user is not None:
            login(request, user)
            return redirect('mural') # Redireciona para o mural após o login
        else:
            messages.error(request, "Usuário ou senha incorretos!")
            return render(request, 'longa.html')

    return render(request, 'longa.html')
@login_required # Garante que só quem logou veja o mural
def mural(request):
    if request.method == "POST":
        # Pega os dados do formulário HTML
        equipamento_id = request.POST.get('equipamento')
        sala = request.POST.get('sala')
        horario = request.POST.get('horario')
        data = request.POST.get('data')

        # Cria a reserva no banco
        Equip = Equipamento.objects.get(id=equipamento_id)
        Reserva.objects.create(
            professor=request.user,
            equipamento=Equip,
            sala=sala,
            periodo=horario,
            data_uso=data
        )
        return redirect('mural')

    # Busca todos os equipamentos e todas as reservas para mostrar na tela
    equipamentos = Equipamento.objects.all()
    reservas = Reserva.objects.all().order_by('-id') # Mais novas primeiro
    
    return render(request, 'mural.html', {'equipamentos': equipamentos, 'reservas': reservas})