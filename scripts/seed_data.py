import os
import django
import random
from datetime import datetime, timedelta
from django.utils import timezone
from faker import Faker

# Configuração do ambiente Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'configuration.settings')
django.setup()

# Importação atualizada: Plano agora é Categoria
from jetfast.models import Veiculo, Lavagem, Categoria, ModeloVeiculo, Marca, Colaborador

fake = Faker('pt_BR')  # Usando localidade Brasil para nomes e placas mais realistas


def criar_dados_teste(n=100):
    print(f"Iniciando a criação de {n} registros...")

    # 1. Garantir que existam categorias
    categorias = list(Categoria.objects.all())
    if not categorias:
        print("Criando categorias básicas...")
        for nome in ['Pequeno', 'Médio', 'SUV', 'Picape']:
            categorias.append(Categoria.objects.create(nome=nome))

    # 2. Garantir que existam colaboradores para as lavagens
    colaboradores = list(Colaborador.objects.all())
    if not colaboradores:
        print("Criando colaboradores...")
        for _ in range(5):
            colaboradores.append(Colaborador.objects.create(nome=fake.name()))

    # 3. Garantir que existam modelos e marcas
    marcas = list(Marca.objects.all())
    if not marcas:
        for m in ['Toyota', 'Ford', 'Volkswagen', 'Fiat', 'Chevrolet']:
            marcas.append(Marca.objects.create(nome=m))

    modelos = list(ModeloVeiculo.objects.all())
    if not modelos:
        for _ in range(10):
            modelos.append(ModeloVeiculo.objects.create(
                nome=fake.word().capitalize(),
                marca=random.choice(marcas)
            ))

    # 4. Criar ou atualizar veículos fictícios
    veiculos = list(Veiculo.objects.all())
    if len(veiculos) < 20:
        print("Criando veículos fictícios...")
        for _ in range(20):
            # Formato de placa Mercosul ou antigo
            placa = fake.bothify(text='???#?##').upper()
            veiculos.append(Veiculo.objects.create(
                placa=placa,
                nome=fake.name(),
                telefone=fake.cellphone_number(),
                modelo_veiculo=random.choice(modelos),
                categoria=random.choice(categorias)
            ))

    # 5. Gerar lavagens com fluxos de horários realistas
    print(f"Gerando {n} lavagens...")
    for i in range(n):
        # Data aleatória nos últimos 30 dias
        dias_atras = random.randint(0, 30)
        data_base = timezone.now() - timedelta(days=dias_atras)

        # Horário de chegada aleatório entre 08:00 e 18:00
        chegada = data_base.replace(hour=random.randint(8, 17), minute=random.randint(0, 59))

        v = random.choice(veiculos)

        # Simula o fluxo: Fila -> Pista -> Saída
        lavagem = Lavagem.objects.create(
            veiculo=v,
            horario_chegada=chegada,
            colaborador_externa=random.choice(colaboradores),
            colaborador_interna=random.choice(colaboradores) if random.random() > 0.3 else None
        )

        # 80% das lavagens já entraram na pista
        if random.random() > 0.2:
            lavagem.horario_pista = chegada + timedelta(minutes=random.randint(10, 60))

            # Dessas, 90% já foram finalizadas
            if random.random() > 0.1:
                lavagem.horario_saida = lavagem.horario_pista + timedelta(minutes=random.randint(30, 90))

        lavagem.save()

        if i % 10 == 0:
            print(f"Registro {i} criado...")

    print(f"Sucesso! Dados inseridos com sucesso.")


if __name__ == '__main__':
    criar_dados_teste(50)