from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='longa'),
    path('criar/', views.CriarConta, name='index'  ),
    path('entrar/', views.Entrar, name='longa'),
    path('Logar/', views.mural, name='mural' ),
    path(
        'exportar-excel/',
        views.exportar_reservas_excel,
        name='exportar_excel'
    ),
    path('ajax/disponiveis/', views.listar_disponiveis, name='ajax_disponiveis'),
    path('ajax/mural-filtrado/', views.carregar_mural, name='ajax_mural'),
]