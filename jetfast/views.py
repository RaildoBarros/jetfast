from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from .models import Veiculo, Lavagem, Colaborador
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.db.models import Q
import json


def detalhes_veiculo(request, pk):
    veiculo = get_object_or_404(Veiculo, pk=pk)
    colaboradores = Colaborador.objects.all()

    lavagens_realizadas = Lavagem.objects.filter(
        veiculo=veiculo
    ).order_by('-horario_chegada')

    return render(request, 'admin/detalhes_veiculo.html', {
        'veiculo': veiculo,
        'lavagens_realizadas': lavagens_realizadas,
        'colaboradores_list': colaboradores,
    })


def registrar_lavagem(request, pk):
    veiculo = get_object_or_404(Veiculo, id=pk)

    if request.method == 'POST':
        # Registro direto, sem validação de quantidade
        Lavagem.objects.create(veiculo=veiculo, horario_chegada=timezone.now())
        messages.success(request, "Veículo adicionado à fila!")

    return redirect('detalhes_veiculo', pk=pk)


def mover_para_pista(request, lavagem_id):
    if request.method == 'POST':
        lavagem = get_object_or_404(Lavagem, id=lavagem_id)
        horario = request.POST.get('horario_custom')

        if horario:
            horario_naive = parse_datetime(horario)
            lavagem.horario_pista = timezone.make_aware(horario_naive) if horario_naive else timezone.now()
        else:
            lavagem.horario_pista = timezone.now()

        lavagem.colaborador_externa_id = request.POST.get('colaborador_externa')
        lavagem.colaborador_interna_id = request.POST.get('colaborador_interna')
        lavagem.save()
        return redirect('acompanhamento_lavagens')


def finalizar_lavagem(request, lavagem_id):
    if request.method == 'POST':
        lavagem = get_object_or_404(Lavagem, id=lavagem_id)
        horario = request.POST.get('horario_custom')

        if horario:
            horario_naive = parse_datetime(horario)
            lavagem.horario_saida = timezone.make_aware(horario_naive) if horario_naive else timezone.now()
        else:
            lavagem.horario_saida = timezone.now()

        lavagem.save()
        return redirect('acompanhamento_lavagens')


def acompanhamento_lavagens(request):
    hoje = timezone.now().date()
    lavagens_hoje = Lavagem.objects.filter(horario_chegada__date=hoje)

    colaboradores = Colaborador.objects.filter(ativo=True).order_by('nome')

    # Contabilização precisa
    total_hoje = lavagens_hoje.count()
    em_fila = lavagens_hoje.filter(horario_pista__isnull=True).count()
    na_pista = lavagens_hoje.filter(horario_pista__isnull=False, horario_saida__isnull=True).count()
    concluidos = lavagens_hoje.filter(horario_saida__isnull=False).count()

    # Ordenação para os cards
    lavagens = lavagens_hoje.order_by('horario_saida', 'horario_pista', 'horario_chegada')

    return render(request, 'admin/acompanhamento.html', {
        'lavagens': lavagens,
        'colaboradores_list': colaboradores,
        'stats': {
            'total': total_hoje,
            'fila': em_fila,
            'pista': na_pista,
            'concluidos': concluidos
        }
    })


# ========================================
# API Endpoints para o Popup
# ========================================

@require_http_methods(["GET"])
def buscar_veiculo(request):
    """Busca veículo pela placa"""
    placa = request.GET.get('placa', '').strip().upper()

    if not placa:
        return JsonResponse({
            'success': False,
            'message': 'Placa não fornecida'
        })

    try:
        veiculo = Veiculo.objects.select_related('modelo_veiculo__marca', 'categoria').get(placa=placa)
        return JsonResponse({
            'success': True,
            'veiculo': {
                'id': veiculo.id,
                'placa': veiculo.placa,
                'nome': veiculo.nome,
                'telefone': veiculo.telefone,
                'modelo': f"{veiculo.modelo_veiculo.marca.nome} {veiculo.modelo_veiculo.nome}",
                'categoria': veiculo.categoria.nome if veiculo.categoria else 'Sem categoria'
            }
        })
    except Veiculo.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': f'Veículo com placa {placa} não encontrado'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': 'Erro ao buscar veículo'
        }, status=500)


@require_http_methods(["POST"])
def criar_lavagem(request):
    """Cria uma nova lavagem"""
    try:
        data = json.loads(request.body)
        veiculo_id = data.get('veiculo_id')
        horario_chegada_str = data.get('horario_chegada')

        if not veiculo_id or not horario_chegada_str:
            return JsonResponse({
                'success': False,
                'message': 'Dados incompletos'
            })

        veiculo = get_object_or_404(Veiculo, id=veiculo_id)

        # Parse do horário
        horario_naive = parse_datetime(horario_chegada_str)
        if horario_naive:
            horario_chegada = timezone.make_aware(horario_naive)
        else:
            horario_chegada = timezone.now()

        # Cria a lavagem
        lavagem = Lavagem.objects.create(
            veiculo=veiculo,
            horario_chegada=horario_chegada
        )

        return JsonResponse({
            'success': True,
            'message': 'Lavagem registrada com sucesso',
            'lavagem_id': lavagem.id
        })

    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Dados inválidos'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Erro ao criar lavagem: {str(e)}'
        }, status=500)