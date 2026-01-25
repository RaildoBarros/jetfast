from django.urls import path
from . import views

urlpatterns = [
    path('', views.detalhes_veiculo, name='detalhes_veiculo_root'),  # Fallback
    path('veiculo/<int:pk>/', views.detalhes_veiculo, name='detalhes_veiculo'),
    path('veiculo/<int:pk>/lavar/', views.registrar_lavagem, name='registrar_lavagem'),

    # Novas rotas para o fluxo
    path('lavagem/<int:lavagem_id>/pista/', views.mover_para_pista, name='mover_para_pista'),
    path('lavagem/<int:lavagem_id>/finalizar/', views.finalizar_lavagem, name='finalizar_lavagem'),
    path('acompanhamento/', views.acompanhamento_lavagens, name='acompanhamento_lavagens'),
]