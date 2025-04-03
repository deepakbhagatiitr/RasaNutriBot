from locust import HttpUser, task, between

class RasaUser(HttpUser):
    host = "http://localhost:5005"  # Set the Rasa host
    wait_time = between(1, 3)  # Users wait between 1 to 3 seconds before sending a new request

    @task
    def send_message(self):
        self.client.post("/webhooks/rest/webhook", json={"sender": "user", "message": "Suggest a high-protein meal"})
