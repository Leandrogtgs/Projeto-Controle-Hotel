from django.db import models

from django.contrib.auth.models import User

class Contato(models.Model):
    nome = models.CharField(max_length=100)
    telefone = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.nome} - {self.telefone}" 


class RegistroConsumo(models.Model):
    TIPO_CHOICES = [
        ('Água', 'Água'),
        ('Gás', 'Gás'),
        ('Eletricidade', 'eletricidade'),
    ]

    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    consumo = models.FloatField(null=True, blank=True)
    apartamentos = models.IntegerField(null=True, blank=True)
    consumo_por_apartamento = models.FloatField(null=True, blank=True)
    data = models.DateField(auto_now_add=True)
    volume_inicial = models.FloatField(null=True, blank=True)
    volume_atual = models.FloatField(null=True, blank=True)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)

    botija_01 = models.FloatField(null=True, blank=True)
    botija_02 = models.FloatField(null=True, blank=True)
    botija_03 = models.FloatField(null=True, blank=True)
    botija_04 = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"{self.tipo} - {self.data}"



class ConsumoRVN(models.Model):
    tipo = models.CharField(max_length=20)  # 'Água', 'Gás', etc.
    consumo = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    apartamentos = models.IntegerField(null=True, blank=True)
    consumo_por_apartamento = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    data = models.DateField(auto_now_add=True)
    volume_inicial = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    volume_atual = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    class Meta:
        ordering = ['-data']
