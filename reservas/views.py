from django.shortcuts import get_object_or_404, render, redirect
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

        # ATUALIZAR QUANTIDADE DOS EQUIPAMENTOS

        if request.user.is_staff and request.POST.get('equipamento_id'):

            equipamento = Equipamento.objects.get(
                id=request.POST.get('equipamento_id')
            )

            equipamento.quantidade = request.POST.get('quantidade')

            equipamento.save()

            messages.success(request, "Quantidade atualizada com sucesso!")

            return redirect('mural')

        equipamento_id = request.POST.get('equipamento')
        sala = request.POST.get('sala')
        periodo = request.POST.get('periodo') 
        data_reserva = request.POST.get('data')

        professor_reserva = request.user

        # Nova implementação administrador, troca do nome

        if request.user.is_staff and request.POST.get('professor'):
            username_informado = request.POST.get('professor').strip()
            try:
                # Busca o usuário exato no banco de dados
                professor_reserva = User.objects.get(username=username_informado)
            except User.DoesNotExist:
                # Se o professor digitado não existir, cancela e avisa o admin
                messages.error(request, f"Erro: O usuário '{username_informado}' não foi encontrado!")
                return redirect('mural')

        # 1. Verificação de reserva duplicada
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
                    professor=professor_reserva,
                    equipamento=equip_obj,
                    sala=sala,
                    periodo=periodo,
                    data_uso=data_reserva
                )
                messages.success(request, f"Reserva realizada com sucesso para {professor_reserva.username}!")
            except Exception as e:
                messages.error(request, f"Erro ao salvar: {e}")
        
        # Após o POST, redirecionamos para o GET da mesma página para limpar o form
        return redirect('mural')

    
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

@login_required
def excluir_reserva(request, reserva_id):
    reserva = get_object_or_404(Reserva, id=reserva_id)
    
    # Verifica se o usuário é o dono da reserva ou staff
    if request.user == reserva.professor or request.user.is_staff:
        reserva.delete()
        messages.success(request, "Reserva excluída com sucesso!")
    else:
        messages.error(request, "Você não tem permissão para excluir esta reserva.")
            
    return redirect('mural')

def listar_disponiveis(request):
    data_sel = request.GET.get('data')
    periodo_sel = request.GET.get('periodo')
    
    try:
        ocupados = Reserva.objects.filter(
            data_uso=data_sel, 
            periodo=periodo_sel
        ).values_list('equipamento_id', flat=True)
        
        disponiveis = Equipamento.objects.exclude(id__in=ocupados)
        
        data = [{'id': e.id, 'nome': e.nome, 'quantidade': e.quantidade} for e in disponiveis]
        return JsonResponse({'equipamentos': data})
    
    except Exception as e:
        return JsonResponse({'erro': str(e)}, status=500)

def carregar_mural(request):
    data_sel = request.GET.get('data')
    reservas = Reserva.objects.filter(data_uso=data_sel).order_by('periodo')
    # Use o caminho relativo a pasta templates
    return render(request, 'partials/lista_reservas.html', {'reservas': reservas})

#1. View principal que carrega a página de entrada (Mural Geral)
def mural_principal(request):
    # Passamos a data de hoje formatada para preencher o ({{ hoje }}) no seu HTML
    hoje_formatado = date.today().strftime('%d/%m/%Y')
    
    # Busca as reservas de hoje para o primeiro carregamento da página (Server-Side)
    reservas_hoje = Reserva.objects.filter(data_uso=date.today()).order_by('periodo')
    
    contexto = {
        'hoje': hoje_formatado,
        'reservas': reservas_hoje
    }
    return render(request, 'mural_consulta.html', contexto)


# 2. View que o JavaScript (Fetch) vai chamar a cada 30 segundos
def carregar_mural(request):
    data_sel = request.GET.get('data')
    
    # Se por acaso o JavaScript não mandar a data, usamos a de hoje por segurança
    if not data_sel:
        data_sel = date.today()
        
    reservas = Reserva.objects.filter(data_uso=data_sel).order_by('periodo')
    
    # Renderiza apenas o pedaço da tabela/grid
    return render(request, 'partials/lista_reservas_consulta.html', {'reservas': reservas})