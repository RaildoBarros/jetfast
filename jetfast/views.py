from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Veiculo, Lavagem
from django.utils import timezone
from django.db.models import Count
from django.http import JsonResponse, HttpResponse
import calendar
import csv
from django.db.models.functions import TruncMonth


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
    _, ultimo_dia = calendar.monthrange(hoje.year, hoje.month)
    ultimo_dia_mes = hoje.replace(day=ultimo_dia, hour=23, minute=59, second=59)

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

def bi_dashboard(request):
    return render(request, 'admin/bi_dashboard.html')

def bi_dashboard_data(request):
    from django.utils import timezone
    from datetime import timedelta
    # Lavagens por mês
    lavagens_por_mes = (
        Lavagem.objects.annotate(mes=TruncMonth('data_lavagem'))
        .values('mes')
        .annotate(total=Count('id'))
        .order_by('mes')
    )
    # Lavagens por veículo
    lavagens_por_veiculo = (
        Lavagem.objects.values('veiculo__placa', 'veiculo__nome')
        .annotate(total=Count('id'))
        .order_by('-total')[:10]
    )
    # Lavagens por plano
    lavagens_por_plano = (
        Lavagem.objects.values('veiculo__plano__nome')
        .annotate(total=Count('id'))
        .order_by('-total')
    )
    # Veículos cadastrados por mês
    veiculos_por_mes = (
        Veiculo.objects.annotate(mes=TruncMonth('data_cadastro'))
        .values('mes')
        .annotate(total=Count('id'))
        .order_by('mes')
    )
    # --- KPIs ---
    # 1. Taxa de Ocupação do Plano
    total_lavagens_possiveis = 0
    total_lavagens_realizadas = 0
    for veiculo in Veiculo.objects.select_related('plano').all():
        lavagens_mes = Lavagem.objects.filter(
            veiculo=veiculo,
            data_lavagem__year=timezone.now().year,
            data_lavagem__month=timezone.now().month
        ).count()
        total_lavagens_realizadas += lavagens_mes
        total_lavagens_possiveis += veiculo.plano.quantidade_lavagens
    taxa_ocupacao = (total_lavagens_realizadas / total_lavagens_possiveis * 100) if total_lavagens_possiveis else 0
    # 2. Churn Rate (veículos sem lavagem há mais de 45 dias)
    dias_churn = 45
    data_limite = timezone.now() - timedelta(days=dias_churn)
    veiculos_sem_lavagem = Veiculo.objects.exclude(lavagem__data_lavagem__gte=data_limite).count()
    total_veiculos = Veiculo.objects.count()
    churn_rate = (veiculos_sem_lavagem / total_veiculos * 100) if total_veiculos else 0
    # 3. Volume por dia da semana
    from django.db.models.functions import ExtractWeekDay
    lavagens_por_dia_semana = (
        Lavagem.objects.annotate(dia_semana=ExtractWeekDay('data_lavagem'))
        .values('dia_semana')
        .annotate(total=Count('id'))
        .order_by('dia_semana')
    )
    # 4. Faturamento estimado (soma dos valores dos planos ativos)
    # Supondo que o valor do plano não está no modelo, retornaremos 0. Se existir, some aqui.
    faturamento_estimado = 0
    data = {
        'lavagens_por_mes': list(lavagens_por_mes),
        'lavagens_por_veiculo': list(lavagens_por_veiculo),
        'lavagens_por_plano': list(lavagens_por_plano),
        'veiculos_por_mes': list(veiculos_por_mes),
        'kpi': {
            'taxa_ocupacao': taxa_ocupacao,
            'churn_rate': churn_rate,
            'faturamento_estimado': faturamento_estimado,
        },
        'lavagens_por_dia_semana': list(lavagens_por_dia_semana),
    }
    return JsonResponse(data)

def bi_dashboard_export_csv(request):
    # Exporta todas as lavagens com dados relevantes
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="lavagens.csv"'
    writer = csv.writer(response)
    writer.writerow(['Placa', 'Nome Veículo', 'Plano', 'Data Lavagem'])
    for lavagem in Lavagem.objects.select_related('veiculo__plano').all():
        writer.writerow([
            lavagem.veiculo.placa,
            lavagem.veiculo.nome,
            lavagem.veiculo.plano.nome,
            lavagem.data_lavagem.strftime('%Y-%m-%d %H:%M'),
        ])
    return response
