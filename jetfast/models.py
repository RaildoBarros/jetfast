from django.db import models
from django.utils import timezone

class Plano(models.Model):
    nome = models.CharField(max_length=100, unique=True)
    quantidade_lavagens = models.IntegerField()

    def __str__(self):
        return self.nome


class Marca(models.Model):
    nome = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nome


class ModeloVeiculo(models.Model):
    marca = models.ForeignKey(Marca, on_delete=models.CASCADE, related_name='modelos')
    nome = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.marca.nome} {self.nome}"


class Veiculo(models.Model):
    placa = models.CharField(max_length=10, unique=True)
    nome = models.CharField(max_length=200)
    modelo_veiculo = models.ForeignKey('ModeloVeiculo', on_delete=models.PROTECT, verbose_name="Veículo")
    plano = models.ForeignKey(Plano, on_delete=models.CASCADE)
    data_cadastro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nome} - {self.placa}"


class Lavagem(models.Model):
    veiculo = models.ForeignKey(Veiculo, on_delete=models.CASCADE)
    data_lavagem = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.veiculo} lavado em {self.data_lavagem.strftime('%d/%m/%Y %H:%M')}"

    class Meta:
        ordering = ['-data_lavagem']