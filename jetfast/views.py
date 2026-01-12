from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Veiculo, Lavagem
from django.utils import timezone
from django.db.models import Count


def detalhes_veiculo(request, pk):
    agora = timezone.now()

    veiculo = get_object_or_404(Veiculo, pk=pk)
    lavagens_realizadas = Lavagem.objects.filter(veiculo=veiculo, data_lavagem__year=agora.year, data_lavagem__month=agora.month).order_by('-data_lavagem')
    quantidade_lavagens_disponiveis = veiculo.plano.quantidade_lavagens - lavagens_realizadas.count()
    return render(request, 'admin/detalhes_veiculo.html', {
        'veiculo': veiculo,
        'lavagens_realizadas': lavagens_realizadas,
        'quantidade_lavagens_disponiveis': quantidade_lavagens_disponiveis,
    })

def registrar_lavagem(request, pk):
    veiculo = get_object_or_404(Veiculo, id=pk)
    hoje = timezone.now()
    primeiro_dia_mes = hoje.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    ultimo_dia_mes = (hoje.replace(day=31) if hoje.month == 12 else hoje.replace(month=hoje.month + 1, day=1)) - timezone.timedelta(days=1)

    lavagens_no_mes = Lavagem.objects.filter(veiculo=veiculo, data_lavagem__gte=primeiro_dia_mes, data_lavagem__lte=ultimo_dia_mes).count()

    if lavagens_no_mes >= veiculo.plano.quantidade_lavagens:
        messages.error(request, "Não há mais lavagens disponíveis no mês.")
        return redirect('detalhes_veiculo', pk=pk)  # Redireciona de volta para a página de detalhes

    if request.method == 'POST':
        # Processar o formulário de adição de lavagem aqui
        nova_lavagem = Lavagem(veiculo=veiculo, data_lavagem=timezone.now())
        nova_lavagem.save()
        messages.success(request, "Lavagem registrada com sucesso.")
        return redirect('detalhes_veiculo', pk=pk)

    # Se a requisição não for POST (ou se houver lavagens disponíveis),
    # você pode renderizar um formulário para adicionar a lavagem (se aplicável)
    # ou simplesmente redirecionar para a página de detalhes com a opção de adicionar.
    return redirect('detalhes_veiculo', pk=pk)