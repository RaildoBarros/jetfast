from locust import HttpUser, task, between

class JetFastUser(HttpUser):
    # O usuário espera entre 1 e 5 segundos entre cada tarefa
    wait_time = between(1, 5)

    @task(3)
    def ver_detalhes(self):
        """Simula a visualização de um veículo específico."""
        # Certifique-se de que o ID 1 existe no seu banco de dados
        self.client.get("/detalhes/1/")

    @task(1)
    def registrar_lavagem(self):
        """Simula o registro de uma lavagem via POST."""
        self.client.post("/registrar/1/")