from django.urls import path
from . import views

urlpatterns = [
    path('', views.detalhes_veiculo, name='detalhes_veiculo'),
    path('veiculo/<int:pk>/', views.detalhes_veiculo, name='detalhes_veiculo'),
    path('veiculo/<int:pk>/lavar/', views.registrar_lavagem, name='registrar_lavagem'),
    path('bi-dashboard/', views.bi_dashboard, name='bi_dashboard'),
    path('bi-dashboard/data/', views.bi_dashboard_data, name='bi_dashboard_data'),
    path('bi-dashboard/export-csv/', views.bi_dashboard_export_csv, name='bi_dashboard_export_csv'),
]