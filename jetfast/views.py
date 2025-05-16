from django.shortcuts import render, redirect, get_object_or_404
from .models import Veiculo, Lavagem
from django.utils import timezone

def detalhes_veiculo(request, pk):
    veiculo = get_object_or_404(Veiculo, pk=pk)
    lavagens_realizadas = Lavagem.objects.filter(veiculo=veiculo).order_by('-data_lavagem')
    quantidade_lavagens_disponiveis = veiculo.plano.quantidade_lavagens - lavagens_realizadas.count()
    return render(request, 'admin/detalhes_veiculo.html', {
        'veiculo': veiculo,
        'lavagens_realizadas': lavagens_realizadas,
        'quantidade_lavagens_disponiveis': quantidade_lavagens_disponiveis,
    })

def registrar_lavagem(request, pk):
    veiculo = get_object_or_404(Veiculo, pk=pk)
    Lavagem.objects.create(veiculo=veiculo, data_lavagem=timezone.now())
    return redirect('detalhes_veiculo', pk=pk)