from django.shortcuts import render, redirect
from .models import Reserva, Equipamento
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.http import HttpResponse
from datetime import date
import openpyxl



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
        return redirect(request,'longa') # Redireciona para a tela de login

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
@login_required
def mural(request):
    # 1. Buscamos os equipamentos FORA do IF do POST 
    # para que eles apareçam assim que a página carregar
    equipamentos = Equipamento.objects.all() 

    if request.method == "POST":
        equipamento_id = request.POST.get('equipamento')
        sala = request.POST.get('sala')
        horario = request.POST.get('horario')
        data = request.POST.get('data')

        # Verificação de reserva duplicada
        ja_reservado = Reserva.objects.filter(
            equipamento_id=equipamento_id, # Usando _id para ser mais direto
            sala=sala, 
            periodo=horario, 
            data_uso=data
        ).exists()

        if ja_reservado:
            messages.error(request, "Horário já reservado!")
            return redirect('mural')

        # Cria a reserva no banco
        try:
            equip_obj = Equipamento.objects.get(id=equipamento_id)
            Reserva.objects.create(
                professor=request.user,
                equipamento=equip_obj,
                sala=sala,
                periodo=horario,
                data_uso=data
            )
            messages.success(request, "Reserva realizada com sucesso!")
        except Exception as e:
            messages.error(request, f"Erro ao salvar: {e}")
        
        return redirect('mural')

    # 2. Buscamos as reservas para mostrar na tabela
    reservas = Reserva.objects.filter(
        data_uso__gte=date.today()
    ).order_by('data_uso', 'periodo')

    # 3. IMPORTANTE: Passamos tanto 'reservas' quanto 'equipamentos' para o HTML
    return render(request, 'mural.html', {
        'reservas': reservas, 
        'equipamentos': equipamentos
    })
@login_required
def excluir_reserva(request, reserva_id):
    if not request.user.is_staff: # Proteção extra: se não for adm, bloqueia
        messages.error(request, "Você não tem permissão para excluir.")
        return redirect('mural')

    reserva = get_object_or_404(Reserva, id=reserva_id)
    reserva.delete()
    messages.success(request, "Reserva excluída com sucesso!")
    return redirect('mural')
    # Busca todos os equipamentos e todas as reservas para mostrar na tela
    quipamentos = Equipamento.objects.all()
    reservas = Reserva.objects.all().order_by('-id') # Mais novas primeiro
    
    return render(request, 'mural.html', {'equipamentos': equipamentos, 'reservas': reservas})
@login_required
def exportar_reservas_excel(request):

    reservas_passadas = Reserva.objects.filter(
        data_uso__lt=date.today()
    ).order_by('-data_uso')

    workbook = openpyxl.Workbook()
    worksheet = workbook.active
    worksheet.title = "Reservas Passadas"

    worksheet.append([
        'Professor',
        'Equipamento',
        'Sala',
        'Periodo',
        'Data'
    ])

    for reserva in reservas_passadas:
        worksheet.append([
            reserva.professor.username,
            reserva.equipamento.nome,
            reserva.sala,
            reserva.periodo,
            str(reserva.data_uso)
        ])

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

    response['Content-Disposition'] = 'attachment; filename=reservas_passadas.xlsx'

    workbook.save(response)

    return response