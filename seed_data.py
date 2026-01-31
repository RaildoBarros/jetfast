import os
import django
import random
from datetime import datetime, timedelta
from django.utils import timezone

# Configuração do ambiente Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'configuration.settings')
django.setup()

from jetfast.models import Veiculo, Lavagem, Categoria, ModeloVeiculo, Marca, Colaborador

# Lista de nomes brasileiros comuns
NOMES = [
    'João Silva', 'Maria Santos', 'Pedro Costa', 'Ana Paula', 'Carlos Eduardo',
    'Juliana Oliveira', 'Rafael Souza', 'Camila Lima', 'Bruno Ferreira', 'Larissa Alves',
    'Lucas Pereira', 'Fernanda Rodrigues', 'Gabriel Martins', 'Patricia Carvalho', 'Rodrigo Gomes',
    'Tatiana Ribeiro', 'Marcelo Dias', 'Vanessa Cardoso', 'Felipe Barbosa', 'Renata Araújo',
    'Diego Monteiro', 'Sabrina Pinto', 'Thiago Freitas', 'Mariana Castro', 'André Moreira',
    'Cristina Mendes', 'Leonardo Soares', 'Amanda Teixeira', 'Ricardo Fernandes', 'Beatriz Rocha'
]

# Marcas e modelos reais
MARCAS_MODELOS = {
    'Toyota': ['Corolla', 'Hilux', 'SW4', 'Yaris', 'Etios'],
    'Volkswagen': ['Gol', 'Polo', 'T-Cross', 'Nivus', 'Amarok', 'Virtus'],
    'Fiat': ['Uno', 'Argo', 'Cronos', 'Toro', 'Strada', 'Mobi'],
    'Chevrolet': ['Onix', 'Tracker', 'S10', 'Cruze', 'Spin'],
    'Ford': ['Ranger', 'Ka', 'EcoSport', 'Territory'],
    'Hyundai': ['HB20', 'Creta', 'Tucson', 'Ix35'],
    'Honda': ['Civic', 'HR-V', 'City', 'Fit'],
    'Renault': ['Sandero', 'Logan', 'Duster', 'Kwid'],
    'Jeep': ['Renegade', 'Compass', 'Commander'],
    'Nissan': ['Kicks', 'Frontier', 'Versa']
}

# CATEGORIAS ATUALIZADAS
CATEGORIAS_PADRAO = ['PRIME', 'EXECUTIVE', 'PREMIUM', 'OFF-ROAD', 'ELITE']

OBSERVACOES = [
    'Cliente solicitou limpeza detalhada',
    'Veículo com muito barro',
    'Aplicar cera especial',
    'Higienização de bancos',
    'Polimento completo',
    'Limpeza de motor',
    'Cliente pediu atenção especial nos detalhes',
    'Veículo vai viajar hoje',
    'Lavagem simples apenas',
    'Cliente regular - atendimento prioritário'
]


def gerar_placa():
    """Gera placa brasileira no formato ABC1234 ou ABC1D23 (Mercosul)"""
    letras = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ', k=3))
    if random.random() > 0.5:
        # Placa antiga: ABC1234
        numeros = ''.join(random.choices('0123456789', k=4))
        return f"{letras}{numeros}"
    else:
        # Placa Mercosul: ABC1D23
        num1 = random.choice('0123456789')
        letra = random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
        num2 = ''.join(random.choices('0123456789', k=2))
        return f"{letras}{num1}{letra}{num2}"


def gerar_telefone():
    """Gera telefone brasileiro no formato 95999999999 (11 dígitos)"""
    ddd = '95'  # DDD de Boa Vista
    numero = '9' + ''.join(random.choices('0123456789', k=8))
    return f"{ddd}{numero}"


def criar_dados_teste(n=100):
    print(f"🚀 Iniciando criação de {n} registros de teste...")
    print("=" * 60)

    # 1. Garantir que existam categorias
    print("\n📋 Verificando categorias...")
    categorias = list(Categoria.objects.all())
    if not categorias:
        print("   Criando categorias padrão...")
        for nome in CATEGORIAS_PADRAO:
            cat = Categoria.objects.create(nome=nome)
            categorias.append(cat)
            print(f"   ✅ Categoria '{nome}' criada")
    else:
        print(f"   ✅ {len(categorias)} categorias encontradas")

    # 2. Garantir que existam colaboradores
    print("\n👥 Verificando colaboradores...")
    colaboradores = list(Colaborador.objects.filter(ativo=True))
    if len(colaboradores) < 5:
        print("   Criando colaboradores...")
        nomes_colaboradores = ['João', 'Maria', 'Pedro', 'Ana', 'Carlos', 'Juliana', 'Rafael']
        for nome in nomes_colaboradores:
            if not Colaborador.objects.filter(nome=nome).exists():
                colab = Colaborador.objects.create(nome=nome, ativo=True)
                colaboradores.append(colab)
                print(f"   ✅ Colaborador '{nome}' criado")
    else:
        print(f"   ✅ {len(colaboradores)} colaboradores encontrados")

    # 3. Garantir que existam marcas e modelos
    print("\n🚗 Verificando marcas e modelos...")
    marcas_dict = {}
    modelos = []

    for marca_nome, lista_modelos in MARCAS_MODELOS.items():
        marca, created = Marca.objects.get_or_create(nome=marca_nome)
        marcas_dict[marca_nome] = marca
        if created:
            print(f"   ✅ Marca '{marca_nome}' criada")

        for modelo_nome in lista_modelos:
            modelo, created = ModeloVeiculo.objects.get_or_create(
                nome=modelo_nome,
                marca=marca
            )
            modelos.append(modelo)
            if created:
                print(f"      ✅ Modelo '{modelo_nome}' criado")

    print(f"   ✅ Total: {len(marcas_dict)} marcas, {len(modelos)} modelos")

    # 4. Criar veículos fictícios
    print(f"\n🚙 Criando veículos...")
    veiculos = list(Veiculo.objects.all())
    veiculos_criados = 0

    # Garantir pelo menos 30 veículos
    while len(veiculos) < 30:
        placa = gerar_placa()

        # Verificar se a placa já existe
        if Veiculo.objects.filter(placa=placa).exists():
            continue

        try:
            veiculo = Veiculo.objects.create(
                placa=placa,
                nome=random.choice(NOMES),
                telefone=gerar_telefone(),
                modelo_veiculo=random.choice(modelos),
                categoria=random.choice(categorias)
            )
            veiculos.append(veiculo)
            veiculos_criados += 1

            if veiculos_criados % 5 == 0:
                print(f"   ✅ {veiculos_criados} veículos criados...")

        except Exception as e:
            print(f"   ⚠️  Erro ao criar veículo: {e}")
            continue

    print(f"   ✅ Total de veículos: {len(veiculos)}")

    # 5. Gerar lavagens com fluxos realistas
    print(f"\n💦 Gerando {n} lavagens...")
    lavagens_criadas = 0

    for i in range(n):
        try:
            # Data aleatória nos últimos 30 dias
            dias_atras = random.randint(0, 30)
            agora = timezone.now()
            data_base = agora - timedelta(days=dias_atras)

            # Horário de chegada aleatório entre 08:00 e 18:00
            hora_chegada = random.randint(8, 17)
            minuto_chegada = random.randint(0, 59)

            chegada = data_base.replace(
                hour=hora_chegada,
                minute=minuto_chegada,
                second=0,
                microsecond=0
            )

            veiculo = random.choice(veiculos)

            # Criar lavagem
            lavagem = Lavagem.objects.create(
                veiculo=veiculo,
                horario_chegada=chegada,
                colaborador_externa=random.choice(colaboradores) if random.random() > 0.1 else None,
                colaborador_interna=random.choice(colaboradores) if random.random() > 0.3 else None,
                observacao=random.choice(OBSERVACOES) if random.random() > 0.5 else None
            )

            # 80% das lavagens já entraram na pista
            if random.random() > 0.2:
                tempo_espera = random.randint(10, 60)
                lavagem.horario_pista = chegada + timedelta(minutes=tempo_espera)

                # Atribuir colaboradores se ainda não tiver
                if not lavagem.colaborador_externa:
                    lavagem.colaborador_externa = random.choice(colaboradores)

                # Dessas, 90% já foram finalizadas
                if random.random() > 0.1:
                    tempo_lavagem = random.randint(30, 90)
                    lavagem.horario_saida = lavagem.horario_pista + timedelta(minutes=tempo_lavagem)

            lavagem.save()
            lavagens_criadas += 1

            if (i + 1) % 10 == 0:
                print(f"   ✅ {i + 1}/{n} lavagens criadas...")

        except Exception as e:
            print(f"   ⚠️  Erro ao criar lavagem {i + 1}: {e}")
            continue

    print(f"\n{'=' * 60}")
    print(f"✨ CONCLUÍDO!")
    print(f"{'=' * 60}")
    print(f"📊 Resumo:")
    print(f"   • Categorias: {len(categorias)}")
    print(f"   • Colaboradores: {len(colaboradores)}")
    print(f"   • Marcas: {len(marcas_dict)}")
    print(f"   • Modelos: {len(modelos)}")
    print(f"   • Veículos: {len(veiculos)}")
    print(f"   • Lavagens criadas: {lavagens_criadas}")
    print(f"{'=' * 60}\n")


if __name__ == '__main__':
    import sys

    # Verificar se passou quantidade como argumento
    quantidade = 100
    if len(sys.argv) > 1:
        try:
            quantidade = int(sys.argv[1])
        except ValueError:
            print("⚠️  Quantidade inválida, usando padrão: 100")

    print(f"\n{'=' * 60}")
    print(f"  SEED DATA - SISTEMA JETFAST")
    print(f"{'=' * 60}\n")

    # Confirmar antes de executar
    resposta = input(f"Criar {quantidade} lavagens de teste? (s/n): ")
    if resposta.lower() in ['s', 'sim', 'y', 'yes']:
        criar_dados_teste(quantidade)
    else:
        print("❌ Operação cancelada.")