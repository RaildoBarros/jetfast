from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Veiculo, Lavagem, Colaborador
from django.utils import timezone
from django.db.models import Count
import calendar


def detalhes_veiculo(request, pk):
    agora = timezone.now()

    colaboradores_list = Colaborador.objects.all()
    veiculo = get_object_or_404(Veiculo, pk=pk)
    lavagens_realizadas = Lavagem.objects.filter(veiculo=veiculo, horario_chegada__year=agora.year, horario_chegada__month=agora.month).order_by('-horario_chegada')
    quantidade_lavagens_disponiveis = veiculo.plano.quantidade_lavagens - lavagens_realizadas.count()
    return render(request, 'admin/detalhes_veiculo.html', {
        'veiculo': veiculo,
        'lavagens_realizadas': lavagens_realizadas,
        'quantidade_lavagens_disponiveis': quantidade_lavagens_disponiveis,
        'colaboradores_list': colaboradores_list,
    })


def registrar_lavagem(request, pk):
    veiculo = get_object_or_404(Veiculo, id=pk)
    hoje = timezone.now()

    # Validação de limite mensal baseada no horário de chegada
    lavagens_no_mes = Lavagem.objects.filter(
        veiculo=veiculo,
        horario_chegada__year=hoje.year,
        horario_chegada__month=hoje.month
    ).count()

    # if lavagens_no_mes >= veiculo.plano.quantidade_lavagens:
    #     messages.error(request, "Não há mais lavagens disponíveis no mês.")
    #     return redirect('detalhes_veiculo', pk=pk)

    if request.method == 'POST':
        # Inicia a lavagem na "Fila"
        Lavagem.objects.create(veiculo=veiculo, horario_chegada=timezone.now())
        messages.success(request, "Veículo colocado na fila com sucesso.")
        return redirect('detalhes_veiculo', pk=pk)

    return redirect('detalhes_veiculo', pk=pk)


def mover_para_pista(request, lavagem_id):
    if request.method == 'POST':
        lavagem = get_object_or_404(Lavagem, id=lavagem_id)
        lavagem.horario_pista = timezone.now()
        lavagem.save()
        messages.info(request, f"Veículo {lavagem.veiculo.placa} entrou na pista.")
        return redirect('detalhes_veiculo', pk=lavagem.veiculo.id)
    return redirect('admin:index')


def finalizar_lavagem(request, lavagem_id):
    if request.method == 'POST':
        lavagem = get_object_or_404(Lavagem, id=lavagem_id)
        lavagem.horario_saida = timezone.now()
        lavagem.save()
        messages.success(request, f"Lavagem do veículo {lavagem.veiculo.placa} finalizada!")
        return redirect('detalhes_veiculo', pk=lavagem.veiculo.id)
    return redirect('admin:index')