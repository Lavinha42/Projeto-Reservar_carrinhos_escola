from django.shortcuts import render, redirect
from .models import Reserva, Equipamento
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.http import HttpResponse
from datetime import date
from django.utils.timezone import now
import openpyxl
from django.http import JsonResponse
from django.utils import timezone




def home(request):
    return render(request, 'longa.html')
def CriarConta(request):
    if request.method == "POST":
        # Pegando os dados do formulário
        usuario = request.POST.get('usuario')
        email = request.POST.get('email')
        senha = request.POST.get('senha')
        confirmar = request.POST.get('confirmar_senha')

        dominio_permitido = "@professor.educacao.sp.gov.br"

        if not email.lower().endswith(dominio_permitido):
            messages.error(request,f"Erro: Apenas e-mails corporativo SEDUC!")
            return render(request,'index.html')
        # 1. Verificar se as senhas batem
        if senha !=  confirmar:
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
        return render(request,'longa.html') # Redireciona para a tela de login
    
        

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
    hoje = now().date()
    
    if request.method == "POST":
        equipamento_id = request.POST.get('equipamento')
        sala = request.POST.get('sala')
        periodo = request.POST.get('periodo') # Ajustado para o nome no HTML
        data_reserva = request.POST.get('data')

        # 1. Verificação de reserva duplicada (Segurança extra)
        ja_reservado = Reserva.objects.filter(
            equipamento_id=equipamento_id, 
            periodo=periodo, 
            data_uso=data_reserva
        ).exists()

        if ja_reservado:
            messages.error(request, "Este carrinho já foi reservado para este horário!")
        else:
            try:
                equip_obj = Equipamento.objects.get(id=equipamento_id)
                Reserva.objects.create(
                    professor=request.user,
                    equipamento=equip_obj,
                    sala=sala,
                    periodo=periodo,
                    data_uso=data_reserva
                )
                messages.success(request, "Reserva realizada com sucesso!")
            except Exception as e:
                messages.error(request, f"Erro ao salvar: {e}")
        
        # Após o POST, redirecionamos para o GET da mesma página para limpar o form
        return redirect('mural')

    # --- Lógica do GET (Carregamento da página) ---
    
    # Buscamos as reservas de HOJE para o mural inicial
    reservas_hoje = Reserva.objects.filter(data_uso=hoje).order_by('periodo')
    
    # Buscamos todos os equipamentos (embora o Ajax vá filtrar depois)
    equipamentos = Equipamento.objects.all()

    return render(request, 'mural.html', {
        'reservas': reservas_hoje,
        'equipamentos': equipamentos,
        'hoje': hoje.strftime('%Y-%m-%d')
    })

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

def limpar_reservas_antigas(request):
    if request.user.is_staff:
        count, _ = Reserva.objects.filter(data_uso__lt=timezone.now().date()).delete()
        messages.success(request, f"{count} reservas antigas foram removidas.")
    return redirect('mural')

def listar_disponiveis(request):
    data_sel = request.GET.get('data')
    periodo_sel = request.GET.get('periodo')
    
    # Busca IDs dos equipamentos que já têm reserva nesse dia e horário
    ocupados = Reserva.objects.filter(
        data_uso=data_sel, 
        periodo=periodo_sel
    ).values_list('equipamento_id', flat=True)
    
    disponiveis = Equipamento.objects.exclude(id__in=ocupados)
    
    data = [{'id': e.id, 'nome': e.nome} for e in disponiveis]
    return JsonResponse({'equipamentos': data})

def carregar_mural(request):
    data_sel = request.GET.get('data')
    reservas = Reserva.objects.filter(data_uso=data_sel).order_by('periodo')
    # Use o caminho relativo a pasta templates
    return render(request, 'partials/lista_reservas.html', {'reservas': reservas})