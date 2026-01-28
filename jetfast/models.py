from django.db import models
from django.utils import timezone
from django.core.validators import RegexValidator


class Colaborador(models.Model):
    nome = models.CharField(max_length=150, unique=True)
    data_cadastro = models.DateTimeField(auto_now_add=True)
    ativo = models.BooleanField(default=True, verbose_name="Ativo")

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = "Colaborador"
        verbose_name_plural = "Colaboradores"
        ordering = ['nome']


class Categoria(models.Model):
    nome = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = "Categoria"
        verbose_name_plural = "Categorias"

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
    # Regex que aceita ABC-1234 ou ABC1D23
    placa_validator = RegexValidator(
        regex=r'^[A-Z]{3}-?\d[A-Z0-9]\d{2}$',
        message="A placa deve estar no formato ABC-1234 ou ABC1D23"
    )

    telefone_validator = RegexValidator(
        regex=r'^\(?\d{2}\)?\s?\d{4,5}-?\d{4}$',
        message="O telefone deve estar no formato (11) 99999-9999 ou 11999999999"
    )

    placa = models.CharField(max_length=8, unique=True, validators=[placa_validator])
    nome = models.CharField(max_length=200)
    telefone = models.CharField(max_length=15, validators=[telefone_validator], help_text="Ex: 11 99999-9999",
                                null=True, blank=True)
    modelo_veiculo = models.ForeignKey('ModeloVeiculo', on_delete=models.PROTECT, verbose_name="Veículo")
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.CASCADE,
        verbose_name="Categoria",
        null=True,
        blank=True
    )
    data_cadastro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nome} - {self.placa}"


class Lavagem(models.Model):
    veiculo = models.ForeignKey(Veiculo, on_delete=models.CASCADE)
    colaborador_externa = models.ForeignKey(
        Colaborador,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='lavagens_externas',
        verbose_name="Colaborador (Externa)"
    )
    colaborador_interna = models.ForeignKey(
        Colaborador,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='lavagens_internas',
        verbose_name="Colaborador (Interna)"
    )
    horario_chegada = models.DateTimeField(default=timezone.now, verbose_name="Chegada (Fila)")
    horario_pista = models.DateTimeField(null=True, blank=True, verbose_name="Início (Pista)")
    horario_saida = models.DateTimeField(null=True, blank=True, verbose_name="Fim (Saída)")
    observacao = models.TextField(null=True, blank=True, verbose_name="Observação")

    def __str__(self):
        status = "Em fila"
        if self.horario_saida:
            status = "Finalizado"
        elif self.horario_pista:
            status = "Na Pista"
        return f"{self.veiculo.placa} - {status} ({self.horario_chegada.strftime('%d/%m')})"

    class Meta:
        ordering = ['-horario_chegada']
        verbose_name_plural = "Lavagens"