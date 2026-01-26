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
    path('api/buscar-veiculo/', views.buscar_veiculo, name='api_buscar_veiculo'),
    path('api/criar-lavagem/', views.criar_lavagem, name='api_criar_lavagem'),
]