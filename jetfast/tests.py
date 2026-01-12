from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.messages import get_messages
from .models import Plano, Marca, ModeloVeiculo, Veiculo, Lavagem
from django.utils import timezone


class LavagemViewsTestCase(TestCase):
    def setUp(self):
        # Configuração inicial dos dados
        self.client = Client()
        self.plano = Plano.objects.create(nome="Plano Básico", quantidade_lavagens=2)
        self.marca = Marca.objects.create(nome="Fiat")
        self.modelo = ModeloVeiculo.objects.create(marca=self.marca, nome="Uno")
        self.veiculo = Veiculo.objects.create(
            placa="ABC1234",
            nome="Carro de Teste",
            modelo_veiculo=self.modelo,
            plano=self.plano
        )
        self.url = reverse('registrar_lavagem', kwargs={'pk': self.veiculo.pk})

    def test_registrar_lavagem_sucesso(self):
        """Testa se uma lavagem é registrada com sucesso quando há saldo."""
        response = self.client.post(self.url)

        # Verifica se redirecionou para detalhes
        self.assertRedirects(response, reverse('detalhes_veiculo', kwargs={'pk': self.veiculo.pk}))

        # Verifica se criou no banco
        self.assertEqual(Lavagem.objects.count(), 1)

        # Verifica mensagem de sucesso
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), "Lavagem registrada com sucesso.")

    def test_bloqueio_limite_lavagens_excedido(self):
        """Testa se o sistema impede o registro após atingir o limite do plano."""
        # Criamos lavagens para atingir o limite (2 lavagens)
        Lavagem.objects.create(veiculo=self.veiculo)
        Lavagem.objects.create(veiculo=self.veiculo)

        # Tenta registrar a terceira lavagem
        response = self.client.post(self.url)

        # Não deve ter criado a terceira no banco
        self.assertEqual(Lavagem.objects.count(), 2)

        # Verifica mensagem de erro
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), "Não há mais lavagens disponíveis no mês.")

    def test_lavagens_meses_diferentes(self):
        """Testa se lavagens de meses anteriores não interferem no limite do mês atual."""
        # Criamos uma lavagem de um mês atrás manualmente
        data_antiga = timezone.now() - timezone.timedelta(days=40)
        lavagem_antiga = Lavagem.objects.create(veiculo=self.veiculo)
        # Forçamos a data no banco (já que auto_now_add impede mudar no .create)
        Lavagem.objects.filter(id=lavagem_antiga.id).update(data_lavagem=data_antiga)

        # O limite é 2. Com uma lavagem antiga, ainda deve permitir 2 no mês atual.
        self.client.post(self.url)  # 1ª do mês atual
        response = self.client.post(self.url)  # 2ª do mês atual

        self.assertEqual(Lavagem.objects.filter(veiculo=self.veiculo).count(), 3)  # 1 antiga + 2 novas
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), "Lavagem registrada com sucesso.")

    def test_detalhes_veiculo_status_code(self):
        """Verifica se a página de detalhes carrega com sucesso (200)."""
        response = self.client.get(reverse('detalhes_veiculo', kwargs={'pk': self.veiculo.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin/detalhes_veiculo.html')

    def test_calculo_lavagens_disponiveis_no_contexto(self):
        """Verifica se o cálculo de lavagens restantes enviado ao template está correto."""
        # O plano permite 2 lavagens. Vamos realizar 1.
        Lavagem.objects.create(veiculo=self.veiculo)

        response = self.client.get(reverse('detalhes_veiculo', kwargs={'pk': self.veiculo.pk}))

        # O contexto deve indicar que ainda resta 1 lavagem (2 - 1 = 1)
        self.assertEqual(response.context['quantidade_lavagens_disponiveis'], 1)
        self.assertEqual(len(response.context['lavagens_realizadas']), 1)

    def test_detalhes_veiculo_404_inexistente(self):
        """Verifica se retorna 404 ao tentar acessar um veículo que não existe."""
        url_invalida = reverse('detalhes_veiculo', kwargs={'pk': 999})
        response = self.client.get(url_invalida)
        self.assertEqual(response.status_code, 404)