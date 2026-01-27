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
def buscar_veiculos(request):
    """Busca veículos por placa, proprietário, telefone ou marca"""
    termo = request.GET.get('termo', '').strip().upper()

    if not termo or len(termo) < 2:
        return JsonResponse({
            'success': False,
            'message': 'Digite pelo menos 2 caracteres'
        })

    try:
        # Busca em múltiplos campos
        veiculos = Veiculo.objects.select_related(
            'modelo_veiculo__marca',
            'categoria'
        ).filter(
            Q(placa__icontains=termo) |
            Q(nome__icontains=termo) |
            Q(telefone__icontains=termo) |
            Q(modelo_veiculo__marca__nome__icontains=termo) |
            Q(modelo_veiculo__nome__icontains=termo)
        )[:10]  # Limita a 10 resultados

        resultados = []
        for veiculo in veiculos:
            resultados.append({
                'id': veiculo.id,
                'placa': veiculo.placa,
                'nome': veiculo.nome,
                'telefone': veiculo.telefone or '',
                'modelo': f"{veiculo.modelo_veiculo.marca.nome} {veiculo.modelo_veiculo.nome}",
                'categoria': veiculo.categoria.nome if veiculo.categoria else 'Sem categoria'
            })

        return JsonResponse({
            'success': True,
            'veiculos': resultados
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': 'Erro ao buscar veículos'
        }, status=500)


@require_http_methods(["GET"])
def listar_marcas(request):
    """Lista todas as marcas disponíveis"""
    try:
        from .models import Marca
        marcas = Marca.objects.all().order_by('nome')

        return JsonResponse({
            'success': True,
            'marcas': [{'id': m.id, 'nome': m.nome} for m in marcas]
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': 'Erro ao carregar marcas'
        }, status=500)


@require_http_methods(["GET"])
def listar_modelos(request):
    """Lista modelos de uma marca específica"""
    marca_id = request.GET.get('marca_id')

    if not marca_id:
        return JsonResponse({
            'success': False,
            'message': 'Marca não especificada'
        })

    try:
        from .models import ModeloVeiculo
        modelos = ModeloVeiculo.objects.filter(marca_id=marca_id).order_by('nome')

        return JsonResponse({
            'success': True,
            'modelos': [{'id': m.id, 'nome': m.nome} for m in modelos]
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': 'Erro ao carregar modelos'
        }, status=500)


@require_http_methods(["GET"])
def listar_categorias(request):
    """Lista todas as categorias disponíveis"""
    try:
        from .models import Categoria
        categorias = Categoria.objects.all().order_by('nome')

        return JsonResponse({
            'success': True,
            'categorias': [{'id': c.id, 'nome': c.nome} for c in categorias]
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': 'Erro ao carregar categorias'
        }, status=500)


@require_http_methods(["POST"])
def criar_veiculo(request):
    """Cria um novo veículo"""
    try:
        data = json.loads(request.body)

        placa = data.get('placa', '').strip().upper()
        nome = data.get('nome', '').strip()
        telefone = data.get('telefone', '').strip()
        modelo_veiculo_id = data.get('modelo_veiculo_id')
        categoria_id = data.get('categoria_id')

        if not placa or not nome or not modelo_veiculo_id:
            return JsonResponse({
                'success': False,
                'message': 'Dados incompletos. Preencha placa, nome e modelo.'
            })

        # Verifica se a placa já existe
        if Veiculo.objects.filter(placa=placa).exists():
            return JsonResponse({
                'success': False,
                'message': f'Já existe um veículo cadastrado com a placa {placa}'
            })

        # Cria o veículo
        from .models import ModeloVeiculo, Categoria

        veiculo = Veiculo.objects.create(
            placa=placa,
            nome=nome,
            telefone=telefone if telefone else None,
            modelo_veiculo_id=modelo_veiculo_id,
            categoria_id=categoria_id if categoria_id else None
        )

        return JsonResponse({
            'success': True,
            'message': 'Veículo cadastrado com sucesso',
            'veiculo_id': veiculo.id
        })

    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Dados inválidos'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Erro ao cadastrar veículo: {str(e)}'
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


@require_http_methods(["GET"])
def obter_lavagem(request, lavagem_id):
    """Obtém os dados de uma lavagem específica"""
    try:
        lavagem = Lavagem.objects.select_related('veiculo', 'colaborador_externa', 'colaborador_interna').get(
            id=lavagem_id)

        return JsonResponse({
            'success': True,
            'lavagem': {
                'id': lavagem.id,
                'veiculo': {
                    'id': lavagem.veiculo.id,
                    'placa': lavagem.veiculo.placa,
                    'nome': lavagem.veiculo.nome
                },
                'horario_chegada': lavagem.horario_chegada.strftime(
                    '%Y-%m-%dT%H:%M') if lavagem.horario_chegada else '',
                'horario_pista': lavagem.horario_pista.strftime('%Y-%m-%dT%H:%M') if lavagem.horario_pista else '',
                'horario_saida': lavagem.horario_saida.strftime('%Y-%m-%dT%H:%M') if lavagem.horario_saida else '',
                'colaborador_externa_id': lavagem.colaborador_externa.id if lavagem.colaborador_externa else None,
                'colaborador_interna_id': lavagem.colaborador_interna.id if lavagem.colaborador_interna else None
            }
        })
    except Lavagem.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Lavagem não encontrada'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': 'Erro ao obter lavagem'
        }, status=500)


@require_http_methods(["POST"])
def atualizar_lavagem(request, lavagem_id):
    """Atualiza os dados de uma lavagem"""
    try:
        data = json.loads(request.body)
        lavagem = get_object_or_404(Lavagem, id=lavagem_id)

        # Atualiza horários
        horario_chegada_str = data.get('horario_chegada')
        if horario_chegada_str:
            horario_naive = parse_datetime(horario_chegada_str)
            if horario_naive:
                lavagem.horario_chegada = timezone.make_aware(horario_naive)

        horario_pista_str = data.get('horario_pista')
        if horario_pista_str:
            horario_naive = parse_datetime(horario_pista_str)
            lavagem.horario_pista = timezone.make_aware(horario_naive) if horario_naive else None
        else:
            lavagem.horario_pista = None

        horario_saida_str = data.get('horario_saida')
        if horario_saida_str:
            horario_naive = parse_datetime(horario_saida_str)
            lavagem.horario_saida = timezone.make_aware(horario_naive) if horario_naive else None
        else:
            lavagem.horario_saida = None

        # Atualiza colaboradores
        colaborador_externa_id = data.get('colaborador_externa_id')
        lavagem.colaborador_externa_id = colaborador_externa_id if colaborador_externa_id else None

        colaborador_interna_id = data.get('colaborador_interna_id')
        lavagem.colaborador_interna_id = colaborador_interna_id if colaborador_interna_id else None

        lavagem.save()

        return JsonResponse({
            'success': True,
            'message': 'Lavagem atualizada com sucesso'
        })

    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Dados inválidos'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Erro ao atualizar lavagem: {str(e)}'
        }, status=500)


@require_http_methods(["POST"])
def excluir_lavagem(request, lavagem_id):
    """Exclui uma lavagem"""
    try:
        lavagem = get_object_or_404(Lavagem, id=lavagem_id)
        lavagem.delete()

        return JsonResponse({
            'success': True,
            'message': 'Lavagem excluída com sucesso'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Erro ao excluir lavagem: {str(e)}'
        }, status=500)


@require_http_methods(["GET"])
def obter_lavagens_hoje(request):
    """Obtém todas as lavagens de hoje com estatísticas"""
    try:
        hoje = timezone.now().date()
        lavagens_hoje = Lavagem.objects.filter(horario_chegada__date=hoje)

        total_hoje = lavagens_hoje.count()
        em_fila = lavagens_hoje.filter(horario_pista__isnull=True).count()
        na_pista = lavagens_hoje.filter(horario_pista__isnull=False, horario_saida__isnull=True).count()
        concluidos = lavagens_hoje.filter(horario_saida__isnull=False).count()

        return JsonResponse({
            'success': True,
            'stats': {
                'total': total_hoje,
                'fila': em_fila,
                'pista': na_pista,
                'concluidos': concluidos
            }
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': 'Erro ao obter dados'
        }, status=500)