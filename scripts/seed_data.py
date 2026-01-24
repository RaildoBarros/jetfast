import os
import django
import random
from datetime import datetime, timedelta
from faker import Faker

# Configuração do ambiente Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'configuration.settings')
django.setup()

from jetfast.models import Veiculo, Lavagem, Plano, ModeloVeiculo, Marca

fake = Faker()

def criar_dados_teste(n=1000):
    print(f"Iniciando a criação de {n} registros...")

    # 1. Garantir que existam planos
    planos = list(Plano.objects.all())
    if not planos:
        print("Crie alguns planos no Admin antes de rodar o script!")
        return

    # 2. Garantir que existam modelos de veículos e marcas
    marcas = list(Marca.objects.all())
    if not marcas:
        for _ in range(5):
            marcas.append(Marca.objects.create(nome=fake.company()))
    modelos = list(ModeloVeiculo.objects.all())
    if not modelos:
        for _ in range(10):
            modelos.append(ModeloVeiculo.objects.create(
                nome=fake.word().capitalize(),
                marca=random.choice(marcas)
            ))

    # 3. Criar veículos fictícios se necessário
    veiculos = list(Veiculo.objects.all())
    placas_existentes = set(v.placa for v in veiculos)
    if len(veiculos) < 50:
        print("Criando veículos fictícios...")
        for _ in range(50 - len(veiculos)):
            placa = fake.unique.bothify(text='???-####').upper()
            while placa in placas_existentes:
                placa = fake.unique.bothify(text='???-####').upper()
            veiculo = Veiculo.objects.create(
                placa=placa,
                nome=fake.first_name(),
                modelo_veiculo=random.choice(modelos),
                plano=random.choice(planos)
            )
            veiculos.append(veiculo)
            placas_existentes.add(placa)

    # 4. Gerar lavagens aleatórias entre 2025 e 2026
    lavagens_para_criar = []
    data_inicio = datetime(2025, 1, 1)
    data_fim = datetime(2026, 12, 31)
    delta_dias = (data_fim - data_inicio).days

    for i in range(n):
        data_aleatoria = data_inicio + timedelta(days=random.randint(0, delta_dias))
        veiculo_sorteado = random.choice(veiculos)
        lavagem = Lavagem(
            veiculo=veiculo_sorteado,
            data_lavagem=data_aleatoria
        )
        lavagens_para_criar.append(lavagem)
        if i % 200 == 0:
            print(f"Preparando registro {i}...")

    Lavagem.objects.bulk_create(lavagens_para_criar)
    print(f"Sucesso! {n} lavagens inseridas no banco.")

if __name__ == '__main__':
    criar_dados_teste(1000)
