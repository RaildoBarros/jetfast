from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.messages import get_messages
from .models import Categoria, Marca, ModeloVeiculo, Veiculo, Lavagem, Colaborador
from django.utils import timezone
from datetime import datetime, time, timedelta
import json


class LavagemViewsTestCase(TestCase):
    def setUp(self):
        """Configuração inicial dos dados para os testes"""
        self.client = Client()

        # Criar categoria
        self.categoria = Categoria.objects.create(nome="Categoria Teste")

        # Criar marca e modelo
        self.marca = Marca.objects.create(nome="Fiat")
        self.modelo = ModeloVeiculo.objects.create(marca=self.marca, nome="Uno")

        # Criar colaboradores
        self.colaborador1 = Colaborador.objects.create(nome="João Silva", ativo=True)
        self.colaborador2 = Colaborador.objects.create(nome="Maria Santos", ativo=True)
        self.colaborador_inativo = Colaborador.objects.create(nome="Pedro Inativo", ativo=False)

        # Criar veículo
        self.veiculo = Veiculo.objects.create(
            placa="ABC1234",
            nome="Cliente Teste",
            telefone="95999999999",
            modelo_veiculo=self.modelo,
            categoria=self.categoria
        )

    def test_detalhes_veiculo_200(self):
        """Testa se a página de detalhes carrega corretamente"""
        response = self.client.get(reverse('detalhes_veiculo', kwargs={'pk': self.veiculo.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin/detalhes_veiculo.html')
        self.assertContains(response, self.veiculo.placa)
        self.assertContains(response, self.veiculo.nome)

    def test_detalhes_veiculo_404(self):
        """Testa se retorna 404 para veículo inexistente"""
        response = self.client.get(reverse('detalhes_veiculo', kwargs={'pk': 9999}))
        self.assertEqual(response.status_code, 404)

    def test_criar_lavagem_via_api(self):
        """Testa criação de lavagem via API"""
        url = reverse('api_criar_lavagem')

        # Horário de teste
        horario_local = timezone.localtime(timezone.now())
        horario_str = horario_local.strftime('%Y-%m-%dT%H:%M')

        data = {
            'veiculo_id': self.veiculo.id,
            'horario_chegada': horario_str,
            'observacao': 'Teste de lavagem'
        }

        response = self.client.post(
            url,
            data=json.dumps(data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertTrue(response_data['success'])
        self.assertEqual(Lavagem.objects.count(), 1)

        # Verificar se a lavagem foi criada corretamente
        lavagem = Lavagem.objects.first()
        self.assertEqual(lavagem.veiculo, self.veiculo)
        self.assertEqual(lavagem.observacao, 'Teste de lavagem')

    def test_criar_lavagem_sem_dados(self):
        """Testa criação de lavagem com dados incompletos"""
        url = reverse('api_criar_lavagem')
        data = {'veiculo_id': self.veiculo.id}  # Falta horario_chegada

        response = self.client.post(
            url,
            data=json.dumps(data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertFalse(response_data['success'])

    def test_acompanhamento_lavagens_hoje(self):
        """Testa se a página de acompanhamento mostra apenas lavagens de hoje"""
        # Criar lavagem de hoje
        lavagem_hoje = Lavagem.objects.create(
            veiculo=self.veiculo,
            horario_chegada=timezone.now()
        )

        # Criar lavagem de ontem
        ontem = timezone.now() - timedelta(days=1)
        lavagem_ontem = Lavagem.objects.create(
            veiculo=self.veiculo,
            horario_chegada=ontem
        )

        response = self.client.get(reverse('acompanhamento_lavagens'))

        self.assertEqual(response.status_code, 200)
        self.assertIn(lavagem_hoje, response.context['lavagens'])
        self.assertNotIn(lavagem_ontem, response.context['lavagens'])

    def test_mover_para_pista(self):
        """Testa mover lavagem para pista com colaboradores"""
        lavagem = Lavagem.objects.create(
            veiculo=self.veiculo,
            horario_chegada=timezone.now()
        )

        url = reverse('mover_para_pista', kwargs={'lavagem_id': lavagem.id})
        horario_local = timezone.localtime(timezone.now())

        response = self.client.post(url, {
            'horario_custom': horario_local.strftime('%Y-%m-%dT%H:%M'),
            'colaborador_externa': self.colaborador1.id,
            'colaborador_interna': self.colaborador2.id
        })

        self.assertEqual(response.status_code, 302)  # Redirect

        lavagem.refresh_from_db()
        self.assertIsNotNone(lavagem.horario_pista)
        self.assertEqual(lavagem.colaborador_externa, self.colaborador1)
        self.assertEqual(lavagem.colaborador_interna, self.colaborador2)

    def test_finalizar_lavagem(self):
        """Testa finalizar lavagem"""
        agora = timezone.now()
        lavagem = Lavagem.objects.create(
            veiculo=self.veiculo,
            horario_chegada=agora,
            horario_pista=agora,
            colaborador_externa=self.colaborador1
        )

        url = reverse('finalizar_lavagem', kwargs={'lavagem_id': lavagem.id})
        horario_local = timezone.localtime(timezone.now())

        response = self.client.post(url, {
            'horario_custom': horario_local.strftime('%Y-%m-%dT%H:%M')
        })

        self.assertEqual(response.status_code, 302)

        lavagem.refresh_from_db()
        self.assertIsNotNone(lavagem.horario_saida)

    def test_obter_lavagem_api(self):
        """Testa API de obtenção de lavagem com conversão de timezone"""
        lavagem = Lavagem.objects.create(
            veiculo=self.veiculo,
            horario_chegada=timezone.now(),
            observacao='Teste observação'
        )

        url = reverse('api_obter_lavagem', kwargs={'lavagem_id': lavagem.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        data = response.json()

        self.assertTrue(data['success'])
        self.assertEqual(data['lavagem']['id'], lavagem.id)
        self.assertEqual(data['lavagem']['veiculo']['placa'], self.veiculo.placa)
        self.assertEqual(data['lavagem']['observacao'], 'Teste observação')

        # Verificar que horários foram formatados corretamente
        self.assertIn('horario_chegada', data['lavagem'])
        self.assertRegex(data['lavagem']['horario_chegada'], r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}')

    def test_atualizar_lavagem_api(self):
        """Testa atualização de lavagem via API"""
        lavagem = Lavagem.objects.create(
            veiculo=self.veiculo,
            horario_chegada=timezone.now()
        )

        url = reverse('api_atualizar_lavagem', kwargs={'lavagem_id': lavagem.id})
        horario_local = timezone.localtime(timezone.now())

        data = {
            'horario_chegada': horario_local.strftime('%Y-%m-%dT%H:%M'),
            'horario_pista': horario_local.strftime('%Y-%m-%dT%H:%M'),
            'colaborador_externa_id': self.colaborador1.id,
            'observacao': 'Observação atualizada'
        }

        response = self.client.post(
            url,
            data=json.dumps(data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertTrue(response_data['success'])

        lavagem.refresh_from_db()
        self.assertIsNotNone(lavagem.horario_pista)
        self.assertEqual(lavagem.colaborador_externa, self.colaborador1)
        self.assertEqual(lavagem.observacao, 'Observação atualizada')

    def test_excluir_lavagem_api(self):
        """Testa exclusão de lavagem via API"""
        lavagem = Lavagem.objects.create(
            veiculo=self.veiculo,
            horario_chegada=timezone.now()
        )

        lavagem_id = lavagem.id
        url = reverse('api_excluir_lavagem', kwargs={'lavagem_id': lavagem_id})

        response = self.client.post(
            url,
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertTrue(response_data['success'])

        # Verificar que foi excluída
        self.assertFalse(Lavagem.objects.filter(id=lavagem_id).exists())

    def test_estatisticas_hoje(self):
        """Testa cálculo de estatísticas do dia"""
        agora = timezone.now()

        # Criar lavagens em diferentes estados
        lavagem_fila = Lavagem.objects.create(
            veiculo=self.veiculo,
            horario_chegada=agora
        )

        lavagem_pista = Lavagem.objects.create(
            veiculo=self.veiculo,
            horario_chegada=agora,
            horario_pista=agora,
            colaborador_externa=self.colaborador1
        )

        lavagem_concluida = Lavagem.objects.create(
            veiculo=self.veiculo,
            horario_chegada=agora,
            horario_pista=agora,
            horario_saida=agora,
            colaborador_externa=self.colaborador1
        )

        response = self.client.get(reverse('acompanhamento_lavagens'))
        stats = response.context['stats']

        self.assertEqual(stats['total'], 3)
        self.assertEqual(stats['fila'], 1)
        self.assertEqual(stats['pista'], 1)
        self.assertEqual(stats['concluidos'], 1)

    def test_buscar_veiculos_api(self):
        """Testa busca de veículos por múltiplos campos"""
        url = reverse('api_buscar_veiculos')

        # Buscar por placa
        response = self.client.get(url, {'termo': 'ABC'})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(len(data['veiculos']), 1)

        # Buscar por nome
        response = self.client.get(url, {'termo': 'Cliente'})
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(len(data['veiculos']), 1)

    def test_criar_veiculo_api(self):
        """Testa criação de veículo via API"""
        url = reverse('api_criar_veiculo')

        data = {
            'placa': 'XYZ9876',
            'nome': 'Novo Cliente',
            'telefone': '95988888888',
            'modelo_veiculo_id': self.modelo.id,
            'categoria_id': self.categoria.id
        }

        response = self.client.post(
            url,
            data=json.dumps(data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertTrue(response_data['success'])

        # Verificar que foi criado
        self.assertTrue(Veiculo.objects.filter(placa='XYZ9876').exists())

    def test_criar_veiculo_placa_duplicada(self):
        """Testa que não permite placa duplicada"""
        url = reverse('api_criar_veiculo')

        data = {
            'placa': self.veiculo.placa,  # Placa já existe
            'nome': 'Outro Cliente',
            'telefone': '95988888888',
            'modelo_veiculo_id': self.modelo.id,
            'categoria_id': self.categoria.id
        }

        response = self.client.post(
            url,
            data=json.dumps(data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertFalse(response_data['success'])
        self.assertIn('já existe', response_data['message'].lower())

    def test_filtro_colaboradores_ativos(self):
        """Testa que apenas colaboradores ativos aparecem no acompanhamento"""
        response = self.client.get(reverse('acompanhamento_lavagens'))
        colaboradores = response.context['colaboradores_list']

        self.assertIn(self.colaborador1, colaboradores)
        self.assertIn(self.colaborador2, colaboradores)
        self.assertNotIn(self.colaborador_inativo, colaboradores)

    def test_lavagem_com_observacao(self):
        """Testa criação e exibição de lavagem com observação"""
        lavagem = Lavagem.objects.create(
            veiculo=self.veiculo,
            horario_chegada=timezone.now(),
            observacao='Cliente pediu cera extra'
        )

        # Verificar no detalhes do veículo
        response = self.client.get(reverse('detalhes_veiculo', kwargs={'pk': self.veiculo.pk}))
        self.assertContains(response, 'Cliente pediu cera extra')

    def test_timezone_conversao_correta(self):
        """Testa que horários são convertidos corretamente para timezone local"""
        # Criar lavagem com horário específico
        agora = timezone.now()
        lavagem = Lavagem.objects.create(
            veiculo=self.veiculo,
            horario_chegada=agora
        )

        # Obter via API
        url = reverse('api_obter_lavagem', kwargs={'lavagem_id': lavagem.id})
        response = self.client.get(url)
        data = response.json()

        # Verificar que o horário retornado está no formato correto
        horario_retornado = data['lavagem']['horario_chegada']
        self.assertRegex(horario_retornado, r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}')

        # Verificar que horário local corresponde
        horario_local = timezone.localtime(agora)
        esperado = horario_local.strftime('%Y-%m-%dT%H:%M')
        self.assertEqual(horario_retornado, esperado)

    def test_lavagens_apenas_hoje(self):
        """Testa que o filtro de hoje funciona corretamente com timezone"""
        # Criar lavagem de hoje
        hoje = timezone.now()
        lavagem_hoje = Lavagem.objects.create(
            veiculo=self.veiculo,
            horario_chegada=hoje
        )

        # Criar lavagem de ontem (subtraindo 25 horas para garantir)
        ontem = hoje - timedelta(hours=25)
        lavagem_ontem = Lavagem.objects.create(
            veiculo=self.veiculo,
            horario_chegada=ontem
        )

        # Obter estatísticas via API
        response = self.client.get(reverse('api_obter_lavagens_hoje'))
        data = response.json()

        self.assertTrue(data['success'])

        # Verificar via view de acompanhamento
        response = self.client.get(reverse('acompanhamento_lavagens'))
        lavagens = response.context['lavagens']

        # Apenas lavagem de hoje deve aparecer
        self.assertIn(lavagem_hoje, lavagens)
        self.assertNotIn(lavagem_ontem, lavagens)

    def test_ordenacao_lavagens(self):
        """Testa ordenação correta das lavagens"""
        # Criar lavagens em ordem diferente
        agora = timezone.now()

        lavagem1 = Lavagem.objects.create(
            veiculo=self.veiculo,
            horario_chegada=agora - timedelta(hours=2)
        )

        lavagem2 = Lavagem.objects.create(
            veiculo=self.veiculo,
            horario_chegada=agora - timedelta(hours=1)
        )

        lavagem3 = Lavagem.objects.create(
            veiculo=self.veiculo,
            horario_chegada=agora
        )

        response = self.client.get(reverse('acompanhamento_lavagens'))
        lavagens = list(response.context['lavagens'])

        # Deve estar ordenado por horário de chegada
        self.assertEqual(lavagens[0], lavagem1)
        self.assertEqual(lavagens[1], lavagem2)
        self.assertEqual(lavagens[2], lavagem3)


class VeiculoModelTestCase(TestCase):
    """Testes do modelo Veiculo"""

    def setUp(self):
        self.marca = Marca.objects.create(nome="Toyota")
        self.modelo = ModeloVeiculo.objects.create(marca=self.marca, nome="Corolla")
        self.categoria = Categoria.objects.create(nome="Médio")

    def test_criar_veiculo_valido(self):
        """Testa criação de veículo com dados válidos"""
        veiculo = Veiculo.objects.create(
            placa="ABC1234",
            nome="João Silva",
            telefone="95999999999",
            modelo_veiculo=self.modelo,
            categoria=self.categoria
        )

        self.assertEqual(veiculo.placa, "ABC1234")
        self.assertEqual(str(veiculo), "João Silva - ABC1234")

    def test_veiculo_sem_telefone(self):
        """Testa que telefone é opcional"""
        veiculo = Veiculo.objects.create(
            placa="XYZ5678",
            nome="Maria Santos",
            modelo_veiculo=self.modelo,
            categoria=self.categoria
        )

        self.assertIsNone(veiculo.telefone)

    def test_veiculo_sem_categoria(self):
        """Testa que categoria é opcional"""
        veiculo = Veiculo.objects.create(
            placa="DEF9012",
            nome="Pedro Costa",
            modelo_veiculo=self.modelo
        )

        self.assertIsNone(veiculo.categoria)


class LavagemModelTestCase(TestCase):
    """Testes do modelo Lavagem"""

    def setUp(self):
        marca = Marca.objects.create(nome="Ford")
        modelo = ModeloVeiculo.objects.create(marca=marca, nome="Ka")
        categoria = Categoria.objects.create(nome="Pequeno")

        self.veiculo = Veiculo.objects.create(
            placa="TEST123",
            nome="Teste",
            modelo_veiculo=modelo,
            categoria=categoria
        )

    def test_criar_lavagem_minima(self):
        """Testa criação de lavagem apenas com veículo"""
        lavagem = Lavagem.objects.create(
            veiculo=self.veiculo,
            horario_chegada=timezone.now()
        )

        self.assertIsNotNone(lavagem.horario_chegada)
        self.assertIsNone(lavagem.horario_pista)
        self.assertIsNone(lavagem.horario_saida)

    def test_status_lavagem(self):
        """Testa representação string do status"""
        agora = timezone.now()

        # Em fila
        lavagem = Lavagem.objects.create(
            veiculo=self.veiculo,
            horario_chegada=agora
        )
        self.assertIn("Em fila", str(lavagem))

        # Na pista
        lavagem.horario_pista = agora
        lavagem.save()
        self.assertIn("Na Pista", str(lavagem))

        # Finalizado
        lavagem.horario_saida = agora
        lavagem.save()
        self.assertIn("Finalizado", str(lavagem))