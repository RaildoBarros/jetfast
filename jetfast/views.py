from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Veiculo, Lavagem, Colaborador
from django.utils import timezone
from django.db.models import Q


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

        lavagem.horario_pista = horario if horario else timezone.now()
        lavagem.colaborador_externa_id = request.POST.get('colaborador_externa')
        lavagem.colaborador_interna_id = request.POST.get('colaborador_interna')
        lavagem.save()
        return redirect('acompanhamento_lavagens')


def finalizar_lavagem(request, lavagem_id):
    if request.method == 'POST':
        lavagem = get_object_or_404(Lavagem, id=lavagem_id)
        horario = request.POST.get('horario_custom')

        lavagem.horario_saida = horario if horario else timezone.now()
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