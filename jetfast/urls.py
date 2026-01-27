from django.urls import path
from . import views

urlpatterns = [
    path('', views.detalhes_veiculo, name='detalhes_veiculo_root'),  # Fallback
    path('veiculo/<int:pk>/', views.detalhes_veiculo, name='detalhes_veiculo'),
    path('veiculo/<int:pk>/lavar/', views.registrar_lavagem, name='registrar_lavagem'),

    # Rotas para o fluxo de lavagem
    path('lavagem/<int:lavagem_id>/pista/', views.mover_para_pista, name='mover_para_pista'),
    path('lavagem/<int:lavagem_id>/finalizar/', views.finalizar_lavagem, name='finalizar_lavagem'),
    path('acompanhamento/', views.acompanhamento_lavagens, name='acompanhamento_lavagens'),

    # API Endpoints para o popup
    path('api/buscar-veiculos/', views.buscar_veiculos, name='api_buscar_veiculos'),
    path('api/criar-lavagem/', views.criar_lavagem, name='api_criar_lavagem'),
    path('api/criar-veiculo/', views.criar_veiculo, name='api_criar_veiculo'),
    path('api/listar-marcas/', views.listar_marcas, name='api_listar_marcas'),
    path('api/listar-modelos/', views.listar_modelos, name='api_listar_modelos'),
    path('api/listar-categorias/', views.listar_categorias, name='api_listar_categorias'),

    # API Endpoints para edição
    path('api/obter-lavagem/<int:lavagem_id>/', views.obter_lavagem, name='api_obter_lavagem'),
    path('api/atualizar-lavagem/<int:lavagem_id>/', views.atualizar_lavagem, name='api_atualizar_lavagem'),
    path('api/excluir-lavagem/<int:lavagem_id>/', views.excluir_lavagem, name='api_excluir_lavagem'),
    path('api/obter-lavagens-hoje/', views.obter_lavagens_hoje, name='api_obter_lavagens_hoje'),
]