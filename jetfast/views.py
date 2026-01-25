from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Veiculo, Lavagem, Colaborador
from django.utils import timezone
from django.db.models import Count
import calendar


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