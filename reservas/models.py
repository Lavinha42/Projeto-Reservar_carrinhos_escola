from django.db import models
from django.contrib.auth.models import User

class Equipamento(models.Model):
    TIPO_CHOICES = [('tablet', 'Carrinho de Tablets'), ('notebook', 'Carrinho de Notebooks')]
    nome = models.CharField("Nome do Carrinho", max_length=100)
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)
    disponivel = models.BooleanField(default=True) # Corrigido
    quantidade = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.nome} ({self.get_tipo_display()})"

class Reserva(models.Model):
    professor = models.ForeignKey(User, on_delete=models.CASCADE)
    equipamento = models.ForeignKey(Equipamento, on_delete=models.CASCADE)
    data_uso = models.DateField("Data da Reserva")
    periodo = models.CharField("Período/Horário", max_length=20)
    sala = models.CharField("Sala", max_length=50, default="") # Adicionado

    def __str__(self):
        return f"{self.professor.username} - {self.equipamento.nome}"