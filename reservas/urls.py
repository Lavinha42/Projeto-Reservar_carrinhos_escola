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
]