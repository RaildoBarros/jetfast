from django.urls import path
from . import views

urlpatterns = [
    path('', views.detalhes_veiculo, name='detalhes_veiculo'),
    path('veiculo/<int:pk>/', views.detalhes_veiculo, name='detalhes_veiculo'),
    path('veiculo/<int:pk>/lavar/', views.registrar_lavagem, name='registrar_lavagem'),
]