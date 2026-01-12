from django.core.management.base import BaseCommand
from jetfast.models import Marca, ModeloVeiculo


class Command(BaseCommand):
    help = 'Popula o banco de dados com uma lista extensa de marcas e modelos'

    def handle(self, *args, **kwargs):
        dados = {
            'Toyota': ['Corolla', 'Hilux', 'SW4', 'Yaris', 'Etios', 'Camry', 'Rav4'],
            'Volkswagen': ['Gol', 'Polo', 'T-Cross', 'Nivus', 'Amarok', 'Jetta', 'Virtus', 'Saveiro', 'Taos'],
            'Fiat': ['Uno', 'Argo', 'Cronos', 'Toro', 'Strada', 'Mobi', 'Pulse', 'Fastback', 'Fiorino'],
            'Chevrolet': ['Onix', 'Tracker', 'S10', 'Cruze', 'Spin', 'Equinox', 'Montana', 'Joy'],
            'Ford': ['Ranger', 'Ka', 'EcoSport', 'Territory', 'Maverick', 'Mustang', 'Bronco'],
            'Hyundai': ['HB20', 'HB20S', 'Creta', 'Tucson', 'Ix35', 'Santa Fe', 'Azera'],
            'Honda': ['Civic', 'HR-V', 'City', 'Fit', 'CR-V', 'WR-V'],
            'Renault': ['Sandero', 'Logan', 'Duster', 'Kwid', 'Oroch', 'Captur', 'Master'],
            'Jeep': ['Renegade', 'Compass', 'Commander', 'Grand Cherokee', 'Wrangler'],
            'Nissan': ['Kicks', 'Frontier', 'Versa', 'Sentra', 'March', 'Leaf'],
            'Mitsubishi': ['L200 Triton', 'Pajero Sport', 'Eclipse Cross', 'Outlander'],
            'Byd': ['Dolphin', 'Seal', 'Song Plus', 'Yuan Plus'],
            'Gwm': ['Haval H6', 'Ora 03'],
            'Bmw': ['Série 3', 'X1', 'X3', 'X5', 'M3'],
            'Mercedes-Benz': ['Classe C', 'GLA', 'GLC', 'GLE', 'Classe A'],
            'Audi': ['A3', 'A4', 'Q3', 'Q5', 'E-Tron'],
        }

        self.stdout.write(self.style.SUCCESS('Iniciando a importação...'))

        for marca_nome, modelos in dados.items():
            marca_obj, created = Marca.objects.get_or_create(nome=marca_nome)
            if created:
                self.stdout.write(f'Marca criada: {marca_nome}')

            for modelo_nome in modelos:
                _, mod_created = ModeloVeiculo.objects.get_or_create(
                    marca=marca_obj,
                    nome=modelo_nome
                )
                if mod_created:
                    self.stdout.write(f'  - Modelo criado: {modelo_nome}')

        self.stdout.write(self.style.SUCCESS('Dados populados com sucesso!'))