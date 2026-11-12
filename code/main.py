import sys
import time
import threading
import tkinter as tk

from api_server import app
from ApiClient import ApiClient
from ApplicationGUI import ApplicationGUI

# Fonction pour demarrer le serveur Flask en arriere-plan
def run_server(port=5000):
    import logging
    # Activer l'affichage des requetes werkzeug (GET, POST, etc.) dans la console
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.INFO)
    app.run(host="127.0.0.1", port=port, debug=False, use_reloader=False)

def main():
    port = 5000
    base_url = f"http://127.0.0.1:{port}"

    # Possibilite de lancer seulement l'API sans interface
    if "--server-only" in sys.argv:
        print("Demarrage du serveur REST seul...")
        print(f"API : {base_url}/api/tickets")
        print(f"Web : {base_url}/web")
        app.run(host="0.0.0.0", port=port, debug=True)
        return

    # Lancement du serveur en arriere-plan s'il ne tourne pas deja
    client = ApiClient(base_url)
    if not client.test_connection():
        print(f"Demarrage du serveur REST sur {base_url}...")
        server_thread = threading.Thread(target=run_server, args=(port,), daemon=True)
        server_thread.start()

        # Attente pour que le serveur soit pret
        for _ in range(20):
            time.sleep(0.1)
            if client.test_connection():
                break

    print("Application prete !")
    print(f"- Serveur API REST : {base_url}/api/tickets")
    print(f"- Interface web bonus : {base_url}/web")

    # Lancement de l'interface Tkinter
    fenetre = tk.Tk()
    app_gui = ApplicationGUI(fenetre, api_client=client)
    fenetre.mainloop()

if __name__ == "__main__":
    main()
