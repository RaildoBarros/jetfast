import os
import django

# Configuração do ambiente Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'configuration.settings')
django.setup()

from jetfast.models import Veiculo, Lavagem, Categoria, ModeloVeiculo, Marca, Colaborador


def limpar_dados_teste():
    """Remove TODOS os dados de teste do banco"""
    
    print("\n" + "=" * 60)
    print("  ⚠️  ATENÇÃO: LIMPEZA DE DADOS DE TESTE")
    print("=" * 60)
    print("\nEsta operação irá EXCLUIR:")
    print("  • Todas as lavagens")
    print("  • Todos os veículos")
    print("  • Todos os colaboradores")
    print("  • Todas as categorias")
    print("  • Todos os modelos de veículos")
    print("  • Todas as marcas")
    print("\n" + "=" * 60)
    
    resposta = input("\n🚨 Tem certeza que deseja EXCLUIR TUDO? Digite 'EXCLUIR' para confirmar: ")
    
    if resposta != 'EXCLUIR':
        print("\n❌ Operação cancelada. Nenhum dado foi excluído.")
        return
    
    print("\n🗑️  Iniciando limpeza...")
    
    # Contadores
    stats = {
        'lavagens': 0,
        'veiculos': 0,
        'colaboradores': 0,
        'categorias': 0,
        'modelos': 0,
        'marcas': 0
    }
    
    # 1. Excluir lavagens
    print("\n💦 Excluindo lavagens...")
    stats['lavagens'] = Lavagem.objects.count()
    Lavagem.objects.all().delete()
    print(f"   ✅ {stats['lavagens']} lavagens excluídas")
    
    # 2. Excluir veículos
    print("\n🚗 Excluindo veículos...")
    stats['veiculos'] = Veiculo.objects.count()
    Veiculo.objects.all().delete()
    print(f"   ✅ {stats['veiculos']} veículos excluídos")
    
    # 3. Excluir colaboradores
    print("\n👥 Excluindo colaboradores...")
    stats['colaboradores'] = Colaborador.objects.count()
    Colaborador.objects.all().delete()
    print(f"   ✅ {stats['colaboradores']} colaboradores excluídos")
    
    # 4. Excluir modelos
    print("\n🚙 Excluindo modelos de veículos...")
    stats['modelos'] = ModeloVeiculo.objects.count()
    ModeloVeiculo.objects.all().delete()
    print(f"   ✅ {stats['modelos']} modelos excluídos")
    
    # 5. Excluir marcas
    print("\n🏷️  Excluindo marcas...")
    stats['marcas'] = Marca.objects.count()
    Marca.objects.all().delete()
    print(f"   ✅ {stats['marcas']} marcas excluídas")
    
    # 6. Excluir categorias
    print("\n📋 Excluindo categorias...")
    stats['categorias'] = Categoria.objects.count()
    Categoria.objects.all().delete()
    print(f"   ✅ {stats['categorias']} categorias excluídas")
    
    # Resumo final
    print("\n" + "=" * 60)
    print("✨ LIMPEZA CONCLUÍDA!")
    print("=" * 60)
    print("\n📊 Total de registros excluídos:")
    print(f"   • Lavagens: {stats['lavagens']}")
    print(f"   • Veículos: {stats['veiculos']}")
    print(f"   • Colaboradores: {stats['colaboradores']}")
    print(f"   • Modelos: {stats['modelos']}")
    print(f"   • Marcas: {stats['marcas']}")
    print(f"   • Categorias: {stats['categorias']}")
    print(f"\n   TOTAL: {sum(stats.values())} registros excluídos")
    print("=" * 60 + "\n")


def limpar_apenas_lavagens():
    """Remove apenas as lavagens, mantendo veículos e outras entidades"""
    
    print("\n" + "=" * 60)
    print("  LIMPEZA PARCIAL: APENAS LAVAGENS")
    print("=" * 60)
    
    total = Lavagem.objects.count()
    print(f"\nSerão excluídas {total} lavagens.")
    print("Veículos, colaboradores e outras entidades serão MANTIDOS.")
    
    resposta = input("\nConfirmar? (s/n): ")
    
    if resposta.lower() not in ['s', 'sim', 'y', 'yes']:
        print("\n❌ Operação cancelada.")
        return
    
    print("\n🗑️  Excluindo lavagens...")
    Lavagem.objects.all().delete()
    print(f"✅ {total} lavagens excluídas com sucesso!\n")


def menu():
    """Menu interativo"""
    print("\n" + "=" * 60)
    print("  GERENCIAMENTO DE DADOS DE TESTE - JETFAST")
    print("=" * 60)
    print("\nEscolha uma opção:")
    print("  1. Limpar TUDO (lavagens, veículos, colaboradores, etc)")
    print("  2. Limpar apenas LAVAGENS (manter veículos e colaboradores)")
    print("  3. Cancelar")
    print("=" * 60)
    
    opcao = input("\nOpção: ")
    
    if opcao == '1':
        limpar_dados_teste()
    elif opcao == '2':
        limpar_apenas_lavagens()
    else:
        print("\n❌ Operação cancelada.\n")


if __name__ == '__main__':
    menu()
