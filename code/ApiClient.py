import os
import requests

# Classe pour communiquer avec le serveur REST (utilise requests)
class ApiClient:
    def __init__(self, base_url: str = "http://127.0.0.1:5000"):
        self.base_url = base_url.rstrip("/")

    # Verifier si le serveur est bien allume
    def test_connection(self) -> bool:
        try:
            res = requests.get(f"{self.base_url}/api/status", timeout=2)
            return res.status_code == 200
        except Exception:
            return False

    # Recuperer les infos de statut du serveur
    def get_status(self) -> dict:
        res = requests.get(f"{self.base_url}/api/status", timeout=3)
        res.raise_for_status()
        return res.json()

    # Recuperer la liste des tickets (avec ou sans filtres)
    def get_tickets(self, status: str = None, priority: str = None) -> list:
        params = {}
        if status:
            params["status"] = status
        if priority:
            params["priority"] = priority

        res = requests.get(f"{self.base_url}/api/tickets", params=params, timeout=5)
        res.raise_for_status()
        return res.json()

    # Trouver un ticket par son identifiant
    def get_ticket(self, ticket_id: int) -> dict:
        res = requests.get(f"{self.base_url}/api/tickets/{ticket_id}", timeout=5)
        res.raise_for_status()
        return res.json()

    # Creer un nouveau ticket (gere aussi l'upload de l'image si specifiee)
    def create_ticket(self, title: str, priority: str, user_id: int, description_texte: str = None, image_path: str = None) -> dict:
        if image_path and os.path.exists(image_path):
            # Envoi avec l'image attachee (multipart)
            data = {
                "title": title,
                "priority": priority,
                "user_id": str(user_id) if user_id is not None else "1",
                "description_texte": description_texte or ""
            }
            with open(image_path, "rb") as f:
                files = {"image": (os.path.basename(image_path), f)}
                res = requests.post(f"{self.base_url}/api/tickets", data=data, files=files, timeout=10)
        else:
            # Envoi simple au format json
            payload = {
                "title": title,
                "priority": priority,
                "user_id": user_id,
                "description_texte": description_texte,
                "description_image": image_path
            }
            res = requests.post(f"{self.base_url}/api/tickets", json=payload, timeout=5)

        res.raise_for_status()
        return res.json()

    # Assigner un ticket a un developpeur
    def assign_ticket(self, ticket_id: int, dev_id: int = None, dev_name: str = None) -> dict:
        payload = {}
        if dev_id is not None:
            payload["dev_id"] = dev_id
        if dev_name:
            payload["dev_name"] = dev_name

        res = requests.put(f"{self.base_url}/api/tickets/{ticket_id}/assign", json=payload, timeout=5)
        res.raise_for_status()
        return res.json()

    # Mettre a jour le statut d'un ticket (VALIDATION, TERMINE, etc.)
    def update_ticket_status(self, ticket_id: int, new_status: str) -> dict:
        payload = {"status": new_status}
        res = requests.put(f"{self.base_url}/api/tickets/{ticket_id}/status", json=payload, timeout=5)
        res.raise_for_status()
        return res.json()

    # Recuperer tous les utilisateurs
    def get_users(self) -> list:
        res = requests.get(f"{self.base_url}/api/users", timeout=5)
        res.raise_for_status()
        return res.json()

    # Creer un utilisateur
    def create_user(self, name: str, email: str) -> dict:
        payload = {"name": name, "email": email}
        res = requests.post(f"{self.base_url}/api/users", json=payload, timeout=5)
        res.raise_for_status()
        return res.json()

    # Recuperer tous les developpeurs
    def get_developpeurs(self) -> list:
        res = requests.get(f"{self.base_url}/api/developpeurs", timeout=5)
        res.raise_for_status()
        return res.json()

    # Creer un developpeur
    def create_developpeur(self, name: str, email: str) -> dict:
        payload = {"name": name, "email": email}
        res = requests.post(f"{self.base_url}/api/developpeurs", json=payload, timeout=5)
        res.raise_for_status()
        return res.json()
