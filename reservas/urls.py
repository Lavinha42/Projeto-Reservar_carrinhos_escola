from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='longa'),
    path('criar/', views.CriarConta, name='index'),
    path('entrar/', views.Entrar, name='longa'),
    path('Logar/', views.mural, name='mural' ),
    path(
        'exportar-excel/',
        views.exportar_reservas_excel,
        name='exportar_excel'
    ),
    path('ajax/mural-filtrado/', views.carregar_mural, name='ajax_mural'),
    path('carregar-mural-publico/', views.carregar_mural_publico, name='carregar_mural_publico'),
    path('ajax/disponiveis/', views.listar_disponiveis, name='ajax_disponiveis'),
    path('painel/', views.mural_principal, name='mural_consulta'),
    path('carregar-mural/', views.carregar_mural, name='carregar_mural'),
    path('excluir-reserva/<int:reserva_id>/', views.excluir_reserva, name='excluir_reserva'),
    path('atualizar-quantidade/', views.atualizar_quantidade, name='atualizar_quantidade'),
]