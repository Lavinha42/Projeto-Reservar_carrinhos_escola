from django.contrib import admin
from .models import Equipamento, Reserva


@admin.register(Equipamento)
class EquipamentoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'tipo','quantidade')


@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = ('professor', 'equipamento', 'data_uso', 'periodo')


