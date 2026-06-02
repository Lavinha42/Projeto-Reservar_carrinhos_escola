from django.shortcuts import get_object_or_404, render, redirect
from .models import Reserva, Equipamento
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.http import HttpResponse
from datetime import date
from django.utils.timezone import datetime, now
import openpyxl
from django.http import JsonResponse
from django.utils import timezone
#novokkk

def home(request):
    return render(request, 'longa.html')

def CriarConta(request):
    if request.method == "POST":
        usuario = request.POST.get('usuario')
        email = request.POST.get('email')
        senha = request.POST.get('senha')
        confirmar = request.POST.get('confirmar_senha')

        dominio_permitido = "@professor.educacao.sp.gov.br"

        if not email.lower().endswith(dominio_permitido):
            messages.error(request, f"Erro: Apenas e-mails corporativo SEDUC!")
            return render(request, 'index.html')

        if senha != confirmar:
            messages.error(request, "As senhas não coincidem!")
            return render(request, 'index.html')

        if User.objects.filter(username=usuario).exists():
            messages.error(request, "Este nome de usuário já está em uso.")
            return render(request, 'index.html')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Este email esta em uso.")
            return render(request, 'index.html')

        user = User.objects.create_user(username=usuario, email=email, password=senha)
        user.save()

        messages.success(request, "Conta criada com sucesso! Faça login.")
        return render(request, 'longa.html')

    return render(request, 'index.html')

def Entrar(request):
    if request.method == "POST":
        usuario_digitado = request.POST.get('usuario')
        senha_digitada = request.POST.get('senha')

        user = authenticate(request, username=usuario_digitado, password=senha_digitada)

        if user is not None:
            login(request, user)
            return redirect('mural')
        else:
            messages.error(request, "Usuário ou senha incorretos!")
            return render(request, 'longa.html')

    return render(request, 'longa.html')

@login_required  # ← CORREÇÃO: removido @login_required duplicado
def mural(request):
    agora = timezone.localtime(timezone.now()) 
    hoje = agora.date()
    hora_atual = agora.time()
    
    # pega a data da URL se existir, senão usa hoje
    data_param = request.GET.get('data')
    data_selecionada = data_param if data_param else hoje.strftime('%Y-%m-%d')

    if request.method == "POST":
        data_reserva_str = request.POST.get('data')
        horario_inicio_str = request.POST.get('horario_inicio')
        data_reservae = datetime.strptime(data_reserva_str, '%Y-%m-%d').date()
        hora_inicioe = datetime.strptime(horario_inicio_str, '%H:%M').time()
        equipamento_id = request.POST.get('equipamento')
        sala = request.POST.get('sala')
        horario_inicio = request.POST.get('horario_inicio')
        horario_fim = request.POST.get('horario_fim')
        data_reserva = request.POST.get('data')

        professor_reserva = request.user

        if data_reservae == hoje and hora_inicioe < hora_atual:
            messages.error(request, "Este horário já passou e não pode ser reservado!")
            return redirect('mural')


        if request.user.is_staff and request.POST.get('professor'):
            username_informado = request.POST.get('professor').strip()
            try:
                professor_reserva = User.objects.get(username=username_informado)
            except User.DoesNotExist:
                messages.error(request, f"Erro: O usuário '{username_informado}' não foi encontrado!")
                return redirect('mural')

        ja_reservado = Reserva.objects.filter(
            equipamento_id=equipamento_id,
            data_uso=data_reserva,
            horario_inicio=horario_inicio,
            horario_fim=horario_fim
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
                    horario_inicio=horario_inicio,
                    horario_fim=horario_fim,
                    data_uso=data_reserva
                )
                messages.success(request, f"Reserva realizada com sucesso para {professor_reserva.username}!")
            except Exception as e:
                messages.error(request, f"Erro ao salvar: {e}")

        return redirect(f"/Logar/?data={data_reserva}")

    reservas_hoje = Reserva.objects.filter(
        data_uso=hoje,
        horario_fim__gte=hora_atual
    ).order_by('horario_inicio')

    equipamentos = Equipamento.objects.all()

    return render(request, 'mural.html', {
        'reservas': reservas_hoje,
        'equipamentos': equipamentos,
        'hoje': data_selecionada,
    })

@login_required
def exportar_reservas_excel(request):
    agora = timezone.localtime(timezone.now())
    hoje = agora.date()
    hora_atual = agora.time()
    reservas_passadas = Reserva.objects.filter(
        data_uso__lt=hoje
    ).union(
        Reserva.objects.filter(
            data_uso = hoje,
            horario_fim__lte = hora_atual
        )
    ).order_by('-data_uso','-horario_fim')

    workbook = openpyxl.Workbook()
    worksheet = workbook.active
    worksheet.title = "Reservas Passadas"

    worksheet.append(['Professor', 'Equipamento', 'Sala', 'Horário', 'Data'])

    for reserva in reservas_passadas:
        worksheet.append([
            reserva.professor.username,
            reserva.equipamento.nome,
            reserva.sala,
            f"{reserva.horario_inicio} - {reserva.horario_fim}",  # ← CORREÇÃO
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

    if request.user == reserva.professor or request.user.is_staff:
        reserva.delete()
        messages.success(request, "Reserva excluída com sucesso!")
    else:
        messages.error(request, "Você não tem permissão para excluir esta reserva.")

    return redirect('mural')

def listar_disponiveis(request):
    data_sel = request.GET.get('data')
    horario_inicio_sel = request.GET.get('horario_inicio')
    horario_fim_sel = request.GET.get('horario_fim')

    try:
        ocupados = Reserva.objects.filter(
            data_uso=data_sel,
            horario_inicio=horario_inicio_sel,
            horario_fim=horario_fim_sel
        ).values_list('equipamento_id', flat=True)

        disponiveis = Equipamento.objects.exclude(id__in=ocupados)
        data = [{'id': e.id, 'nome': e.nome, 'quantidade': e.quantidade} for e in disponiveis]
        return JsonResponse({'equipamentos': data})

    except Exception as e:
        return JsonResponse({'erro': str(e)}, status=500)

# ← CORREÇÃO: apenas uma função carregar_mural, com filtro automático por horário
# Mural do professor (com botão excluir)
def carregar_mural(request):
    data_sel = request.GET.get('data')

    if not data_sel:
        data_sel = date.today().strftime('%Y-%m-%d')

    data_sel_obj = datetime.strptime(data_sel, '%Y-%m-%d').date() if isinstance(data_sel, str) else data_sel

    hora_atual = timezone.now().time()
    hoje = date.today()

    if data_sel_obj == hoje:
        reservas = Reserva.objects.filter(
            data_uso=data_sel_obj,
            horario_fim__gte=hora_atual
        ).order_by('horario_inicio')
    else:
        reservas = Reserva.objects.filter(
            data_uso=data_sel
        ).order_by('horario_inicio')

    return render(request, 'partials/lista_reservas.html', {
        'reservas': reservas,
        'user': request.user,  # ✅ passa o usuário logado
    })


# Mural público (sem botão excluir)
def carregar_mural_publico(request):
    data_sel = request.GET.get('data')

    if not data_sel:
        data_sel = date.today()

    hora_atual = timezone.now().time()
    hoje = date.today()

    if str(data_sel) == str(hoje):
        reservas = Reserva.objects.filter(
            data_uso=data_sel,
            horario_fim__gte=hora_atual
        ).order_by('horario_inicio')
    else:
        reservas = Reserva.objects.filter(
            data_uso=data_sel
        ).order_by('horario_inicio')

    return render(request, 'partials/lista_reservas_consulta.html', {'reservas': reservas})

def mural_principal(request):
    hoje = date.today()
    hora_atual = timezone.now().time()
    data_sel = date.today().strftime('%Y-%m-%d')


    data_sel_obj = datetime.strptime(data_sel, '%Y-%m-%d').date() if isinstance(data_sel, str) else data_sel

    reservas_hoje = Reserva.objects.filter(
        data_uso=data_sel_obj,
        horario_fim__gte=hora_atual
    ).order_by('horario_inicio')

    return render(request, 'mural_consulta.html', {
        'hoje': hoje.strftime('%d/%m/%Y'),
        'reservas': reservas_hoje
    })

#1