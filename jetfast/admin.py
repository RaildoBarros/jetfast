from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from .models import Marca, ModeloVeiculo, Veiculo, Plano, Lavagem, Colaborador

# Single constant for the admin CSS path to avoid duplicating the literal
CSS_ADMIN_PATH = 'admin/css/admin_logo.css'


class Media:
    css = {
        'all': (CSS_ADMIN_PATH,)
    }
admin.site.Media = Media


@admin.register(Plano)
class PlanoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'quantidade_lavagens')
    search_fields = ('nome',)

    class Media:
        css = {
            'all': (CSS_ADMIN_PATH,)
        }

@admin.register(Marca)
class MarcaAdmin(admin.ModelAdmin):
    list_display = ('nome',)
    search_fields = ('nome',)

    class Media:
        css = {
            'all': (CSS_ADMIN_PATH,)
        }

@admin.register(ModeloVeiculo)
class ModeloVeiculoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'marca')
    search_fields = ('nome', 'marca__nome')
    list_filter = ('marca',)

    class Media:
        css = {
            'all': (CSS_ADMIN_PATH,)
        }

@admin.register(Veiculo)
class VeiculoAdmin(admin.ModelAdmin):
    list_display = ('placa', 'nome', 'telefone', 'modelo_veiculo', 'plano', 'ver_detalhes')
    search_fields = ('placa', 'nome', 'telefone', 'modelo_veiculo', 'plano')
    list_filter = ('plano', 'modelo_veiculo')

    def ver_detalhes(self, obj):
        url = reverse('detalhes_veiculo', args=[obj.id])
        return format_html(
            '<a href="{url}" style="display: flex; justify-content: center;"><img src="/static/admin/img/search.svg" alt="Ver Detalhes" style="width: 16px; height: 16px;"></a>',
            url=url,
        )
    ver_detalhes.short_description = 'Detalhes'

    class Media:
        css = {
            'all': (CSS_ADMIN_PATH,)
        }

@admin.register(Lavagem)
class LavagemAdmin(admin.ModelAdmin):
    list_display = (
        'veiculo',
        'colaborador_externa',
        'colaborador_interna',
        'chegada_formatada',
        'pista_formatada',
        'saida_formatada'
    )
    list_filter = ('horario_chegada', 'colaborador_externa', 'colaborador_interna')
    search_fields = ('veiculo__placa', 'veiculo__nome')

    # Métodos para formatar as datas no padrão: 24/01/2026 às 14:58
    def chegada_formatada(self, obj):
        return obj.horario_chegada.strftime('%d/%m/%Y às %H:%M')

    chegada_formatada.short_description = 'Chegada (Fila)'

    def pista_formatada(self, obj):
        if obj.horario_pista:
            return obj.horario_pista.strftime('%d/%m/%Y às %H:%M')
        return "---"

    pista_formatada.short_description = 'Início (Pista)'

    def saida_formatada(self, obj):
        if obj.horario_saida:
            return obj.horario_saida.strftime('%d/%m/%Y às %H:%M')
        return "---"

    saida_formatada.short_description = 'Saída'

    def get_status(self, obj):
        if obj.horario_saida: return "Finalizado"
        if obj.horario_pista: return "Em Pista"
        return "Em Fila"
    get_status.short_description = 'Status'

    class Media:
        css = {'all': (CSS_ADMIN_PATH,)}

@admin.register(Colaborador)
class ColaboradorAdmin(admin.ModelAdmin):
    list_display = ('nome', 'data_cadastro')
    search_fields = ('nome',)