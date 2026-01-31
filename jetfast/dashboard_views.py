from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Count, F, ExpressionWrapper, DurationField, Q
from django.utils import timezone
from datetime import datetime, time, timedelta
from jetfast.models import Lavagem, Categoria, Colaborador


@login_required
def dashboard(request):
    """
    Dashboard principal com indicadores de desempenho e análises
    """
    # Filtros de data (padrão: últimos 30 dias)
    dias_param = request.GET.get('dias', '30')
    data_inicial_custom = request.GET.get('data_inicial')
    data_final_custom = request.GET.get('data_final')

    # Se houver datas customizadas, usa elas
    if data_inicial_custom and data_final_custom:
        from django.utils.dateparse import parse_date
        data_inicio_date = parse_date(data_inicial_custom)
        data_fim_date = parse_date(data_final_custom)

        if data_inicio_date and data_fim_date:
            data_inicio = timezone.make_aware(datetime.combine(data_inicio_date, time.min))
            data_fim = timezone.make_aware(datetime.combine(data_fim_date, time.max))
            dias = (data_fim_date - data_inicio_date).days + 1
            periodo_label = f"{data_inicio_date.strftime('%d/%m/%Y')} até {data_fim_date.strftime('%d/%m/%Y')}"
            modo_filtro = 'custom'
        else:
            # Fallback se as datas forem inválidas
            dias_param = '30'
            data_inicial_custom = None
            data_final_custom = None
            modo_filtro = 'predefinido'
    else:
        modo_filtro = 'predefinido'

    # Filtro predefinido (7, 15, 30, 60, 90 dias ou tudo)
    if modo_filtro == 'predefinido':
        if dias_param == 'tudo':
            dias = None
            data_inicio = None
            data_fim = None
            periodo_label = "Todo o período"
        else:
            dias = int(dias_param)
            data_fim = timezone.now()
            data_inicio = data_fim - timedelta(days=dias)
            periodo_label = f"Últimos {dias} dias"

    # Filtrar lavagens concluídas no período
    if data_inicio and data_fim:
        lavagens = Lavagem.objects.filter(
            horario_chegada__gte=data_inicio,
            horario_chegada__lte=data_fim,
            horario_saida__isnull=False  # Apenas lavagens finalizadas
        ).select_related('veiculo__categoria', 'colaborador_externa', 'colaborador_interna')
    elif data_inicio and not data_fim:
        lavagens = Lavagem.objects.filter(
            horario_chegada__gte=data_inicio,
            horario_saida__isnull=False
        ).select_related('veiculo__categoria', 'colaborador_externa', 'colaborador_interna')
    else:
        lavagens = Lavagem.objects.filter(
            horario_saida__isnull=False  # Apenas lavagens finalizadas
        ).select_related('veiculo__categoria', 'colaborador_externa', 'colaborador_interna')

    # ========================================
    # INDICADORES PRINCIPAIS
    # ========================================
    total_lavagens = lavagens.count()

    # Calcular tempos médios
    lavagens_com_tempos = lavagens.annotate(
        tempo_lavagem=ExpressionWrapper(
            F('horario_saida') - F('horario_pista'),
            output_field=DurationField()
        ),
        tempo_fila=ExpressionWrapper(
            F('horario_pista') - F('horario_chegada'),
            output_field=DurationField()
        ),
        tempo_total=ExpressionWrapper(
            F('horario_saida') - F('horario_chegada'),
            output_field=DurationField()
        )
    )

    # Agregações
    agregacoes = lavagens_com_tempos.aggregate(
        tempo_medio_lavagem=Avg('tempo_lavagem'),
        tempo_medio_fila=Avg('tempo_fila'),
        tempo_medio_total=Avg('tempo_total')
    )

    def formatar_tempo(timedelta_obj):
        """Converte timedelta para formato legível (hh:mm)"""
        if not timedelta_obj:
            return "0:00"
        total_segundos = int(timedelta_obj.total_seconds())
        horas = total_segundos // 3600
        minutos = (total_segundos % 3600) // 60
        return f"{horas}:{minutos:02d}"

    indicadores = {
        'total_lavagens': total_lavagens,
        'tempo_medio_lavagem': formatar_tempo(agregacoes['tempo_medio_lavagem']),
        'tempo_medio_fila': formatar_tempo(agregacoes['tempo_medio_fila']),
        'tempo_medio_total': formatar_tempo(agregacoes['tempo_medio_total'])
    }

    # ========================================
    # GRÁFICO: LAVAGENS POR DIA
    # ========================================
    # Determina quantos dias mostrar no gráfico
    if dias:
        dias_grafico = dias
    else:
        # Se for "tudo", pega a primeira lavagem e calcula até hoje
        primeira_lavagem = Lavagem.objects.filter(horario_saida__isnull=False).order_by('horario_chegada').first()
        if primeira_lavagem:
            dias_grafico = (timezone.now().date() - timezone.localtime(
                primeira_lavagem.horario_chegada).date()).days + 1
            # Limita a 90 dias para não sobrecarregar o gráfico
            dias_grafico = min(dias_grafico, 90)
        else:
            dias_grafico = 30

    lavagens_por_dia = {}
    for i in range(dias_grafico):
        data = (timezone.now() - timedelta(days=dias_grafico - 1 - i)).date()
        lavagens_por_dia[data.strftime('%d/%m')] = 0

    # Contar lavagens por dia
    for lavagem in lavagens:
        data_str = timezone.localtime(lavagem.horario_chegada).date().strftime('%d/%m')
        if data_str in lavagens_por_dia:
            lavagens_por_dia[data_str] += 1

    # Converter para listas separadas (CORREÇÃO DO ERRO)
    lavagens_por_dia_labels = list(lavagens_por_dia.keys())
    lavagens_por_dia_data = list(lavagens_por_dia.values())

    # ========================================
    # GRÁFICO: DISTRIBUIÇÃO POR CATEGORIA
    # ========================================
    lavagens_por_categoria = lavagens.values(
        'veiculo__categoria__nome'
    ).annotate(
        total=Count('id')
    ).order_by('-total')

    distribuicao_categoria = {
        'labels': [item['veiculo__categoria__nome'] or 'Sem Categoria'
                   for item in lavagens_por_categoria],
        'data': [item['total'] for item in lavagens_por_categoria]
    }

    # ========================================
    # GRÁFICO: PRODUTIVIDADE POR COLABORADOR
    # ========================================
    produtividade_colaboradores = lavagens.values(
        'colaborador_externa__nome'
    ).annotate(
        total=Count('id')
    ).order_by('-total')[:10]  # Top 10

    produtividade = {
        'labels': [item['colaborador_externa__nome'] or 'Não Atribuído'
                   for item in produtividade_colaboradores],
        'data': [item['total'] for item in produtividade_colaboradores]
    }

    # ========================================
    # TABELA: ANÁLISE POR CATEGORIA
    # ========================================
    categorias = Categoria.objects.all()
    analise_categorias = []

    for categoria in categorias:
        lavagens_cat = lavagens_com_tempos.filter(veiculo__categoria=categoria)

        agregacoes_cat = lavagens_cat.aggregate(
            total=Count('id'),
            tempo_medio_lavagem=Avg('tempo_lavagem'),
            tempo_medio_fila=Avg('tempo_fila'),
            tempo_medio_total=Avg('tempo_total')
        )

        if agregacoes_cat['total'] > 0:
            analise_categorias.append({
                'categoria': categoria.nome,
                'total_lavagens': agregacoes_cat['total'],
                'tempo_medio_lavagem': formatar_tempo(agregacoes_cat['tempo_medio_lavagem']),
                'tempo_medio_fila': formatar_tempo(agregacoes_cat['tempo_medio_fila']),
                'tempo_medio_total': formatar_tempo(agregacoes_cat['tempo_medio_total'])
            })

    # Adicionar lavagens sem categoria
    lavagens_sem_cat = lavagens_com_tempos.filter(veiculo__categoria__isnull=True)
    agregacoes_sem_cat = lavagens_sem_cat.aggregate(
        total=Count('id'),
        tempo_medio_lavagem=Avg('tempo_lavagem'),
        tempo_medio_fila=Avg('tempo_fila'),
        tempo_medio_total=Avg('tempo_total')
    )

    if agregacoes_sem_cat['total'] > 0:
        analise_categorias.append({
            'categoria': 'Sem Categoria',
            'total_lavagens': agregacoes_sem_cat['total'],
            'tempo_medio_lavagem': formatar_tempo(agregacoes_sem_cat['tempo_medio_lavagem']),
            'tempo_medio_fila': formatar_tempo(agregacoes_sem_cat['tempo_medio_fila']),
            'tempo_medio_total': formatar_tempo(agregacoes_sem_cat['tempo_medio_total'])
        })

    # ========================================
    # ESTATÍSTICAS ADICIONAIS
    # ========================================
    hoje = timezone.localtime(timezone.now()).date()
    inicio_hoje = timezone.make_aware(datetime.combine(hoje, time.min))
    fim_hoje = timezone.make_aware(datetime.combine(hoje, time.max))

    lavagens_hoje = Lavagem.objects.filter(
        horario_chegada__gte=inicio_hoje,
        horario_chegada__lte=fim_hoje
    ).count()

    lavagens_concluidas_hoje = Lavagem.objects.filter(
        horario_chegada__gte=inicio_hoje,
        horario_chegada__lte=fim_hoje,
        horario_saida__isnull=False
    ).count()

    context = {
        'indicadores': indicadores,
        'lavagens_por_dia_labels': lavagens_por_dia_labels,  # CORREÇÃO
        'lavagens_por_dia_data': lavagens_por_dia_data,  # CORREÇÃO
        'distribuicao_categoria': distribuicao_categoria,
        'produtividade': produtividade,
        'analise_categorias': analise_categorias,
        'dias_filtro': dias_param,  # Passa o parâmetro original
        'periodo_label': periodo_label,
        'lavagens_hoje': lavagens_hoje,
        'lavagens_concluidas_hoje': lavagens_concluidas_hoje,
        'modo_filtro': modo_filtro,
        'data_inicial_custom': data_inicial_custom,
        'data_final_custom': data_final_custom,
    }

    return render(request, 'admin/dashboard.html', context)