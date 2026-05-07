from django.db import models
from django.contrib.auth.models import User

class Equipamento(models.Model):
    TIPO_CHOICES = [('tablet', 'Carrinho de Tablets'), ('notebook', 'Carrinho de Notebooks')]
    nome = models.CharField("Nome do Carrinho", max_length=100)
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)

    def __str__(self):
        return f"{self.nome} ({self.get_tipo_display()})"

class Reserva(models.Model):
    professor = models.ForeignKey(User, on_delete=models.CASCADE)
    equipamento = models.ForeignKey(Equipamento, on_delete=models.CASCADE)
    data_uso = models.DateField("Data da Reserva")
    periodo = models.CharField("Período", max_length=20)

    def __str__(self):
        return f"{self.professor} - {self.equipamento}"

# Create your models here.
