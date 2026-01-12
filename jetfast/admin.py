from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from .models import Marca, ModeloVeiculo, Veiculo, Plano, Lavagem


class Media:
    css = {
        'all': ('admin/css/admin_logo.css',)
    }
admin.site.Media = Media


@admin.register(Plano)
class PlanoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'quantidade_lavagens')
    search_fields = ('nome',)

    class Media:
        css = {
            'all': ('admin/css/admin_logo.css',)
        }

@admin.register(Marca)
class MarcaAdmin(admin.ModelAdmin):
    list_display = ('nome',)
    search_fields = ('nome',)

    class Media:
        css = {
            'all': ('admin/css/admin_logo.css',)
        }

@admin.register(ModeloVeiculo)
class ModeloVeiculoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'marca')
    search_fields = ('nome', 'marca__nome')
    list_filter = ('marca',)

    class Media:
        css = {
            'all': ('admin/css/admin_logo.css',)
        }

@admin.register(Veiculo)
class VeiculoAdmin(admin.ModelAdmin):
    list_display = ('placa', 'nome', 'modelo_veiculo', 'plano', 'ver_detalhes')
    search_fields = ('placa', 'nome')
    list_filter = ('plano', 'modelo_veiculo')

    def ver_detalhes(self, obj):
        url = reverse('detalhes_veiculo', args=[obj.id])
        return format_html('<a href="{}" style="display: flex; justify-content: center;"><img src="/static/admin/img/search.svg" alt="Ver Detalhes"     style="width: 16px; height: 16px; "></a>', url)
    ver_detalhes.short_description = 'Detalhes'

    class Media:
        css = {
            'all': ('admin/css/admin_logo.css',)
        }

@admin.register(Lavagem)
class LavagemAdmin(admin.ModelAdmin):
    list_display = ('veiculo', 'data_lavagem')
    list_filter = ('veiculo', 'data_lavagem')
    date_hierarchy = 'data_lavagem'

    class Media:
        css = {
            'all': ('admin/css/admin_logo.css',)
        }