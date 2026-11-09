import os
from datetime import date
from flask import Flask, request, jsonify, send_from_directory, render_template

# Imports des classes metier (Modeles)
from Statut import Statut
from Priorite import Priorite
from TypeDescription import TypeDescription
from DescriptionFactory import DescriptionFactory
from Ticket import Ticket
from User import User
from Developpeur import Developpeur
from GestionnaireTickets import GestionnaireTickets

# Dossiers pour les images et templates
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGES_DIR = os.path.join(BASE_DIR, "images")
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
os.makedirs(IMAGES_DIR, exist_ok=True)
os.makedirs(TEMPLATES_DIR, exist_ok=True)

# Initialisation de l'application Flask
app = Flask(__name__, template_folder=TEMPLATES_DIR)

# Gestionnaire central des tickets pour le serveur
gestionnaire = GestionnaireTickets()

# Initialisation des donnees de test au demarrage
def initialiser_donnees():
    User.prochainId = 1
    Ticket.prochainId = 1
    gestionnaire.tickets.clear()

    # Utilisateurs et developpeurs par defaut
    user1 = User("Alpha", "alpha@uqac.ca")
    user2 = User("Bob", "bob@uqac.ca")
    dev1 = Developpeur("Abdramane", "abdramane@uqac.ca")
    dev2 = Developpeur("Ibrahim", "ibrahim@uqac.ca")

    image_erreur = os.path.join(IMAGES_DIR, "capture_erreur.png")

    # Ticket 1 avec texte et image
    t1 = Ticket(title="Erreur d'affichage au demarrage", priority=Priorite.HAUTE)
    d1_texte = DescriptionFactory.createDescription(
        TypeDescription.TEXTE,
        "L'application plante lors de l'ouverture sur Windows."
    )
    t1.addDescription(d1_texte)
    if os.path.exists(image_erreur):
        d1_image = DescriptionFactory.createDescription(TypeDescription.IMAGE, image_erreur)
        t1.addDescription(d1_image)
    user1.createTicket(t1)
    gestionnaire.ajouter(t1)

    # Ticket 2 avec texte seulement, assigne a dev1
    t2 = Ticket(title="Bouton mal aligne", priority=Priorite.BASSE)
    d2_texte = DescriptionFactory.createDescription(
        TypeDescription.TEXTE,
        "Le bouton Quitter depasse de la fenetre."
    )
    t2.addDescription(d2_texte)
    user2.createTicket(t2)
    dev1.assignTicket(t2, dev1)
    gestionnaire.ajouter(t2)

    return [user1, user2], [dev1, dev2]

utilisateurs_list, developpeurs_list = initialiser_donnees()

# Fonctions utilitaires pour chercher un compte
def trouver_user_par_id(user_id: int):
    for u in utilisateurs_list:
        if u.userId == user_id:
            return u
    for d in developpeurs_list:
        if d.userId == user_id:
            return d
    return None

def trouver_dev_par_id(dev_id: int):
    for d in developpeurs_list:
        if d.userId == dev_id:
            return d
    return None

#----------------------------------------------------------------------
# ROUTES DE L'API REST
#----------------------------------------------------------------------

# Verification de l'etat du serveur
@app.route("/api/status", methods=["GET"])
def api_status():
    return jsonify({
        "status": "online",
        "service": "API REST Gestionnaire de Tickets (UQAC 6GEI311)",
        "tickets_count": len(gestionnaire.tous()),
        "users_count": len(utilisateurs_list),
        "devs_count": len(developpeurs_list)
    }), 200

# Recuperer tous les tickets (avec possibilite de filtrer)
@app.route("/api/tickets", methods=["GET"])
def get_tickets():
    status_filter = request.args.get("status")
    priority_filter = request.args.get("priority")
    user_id_filter = request.args.get("user_id", type=int)

    tickets = gestionnaire.tous()

    # Application des filtres si demandes
    if status_filter:
        tickets = [t for t in tickets if t.status.value.upper() == status_filter.upper() or t.status.name.upper() == status_filter.upper()]
    if priority_filter:
        tickets = [t for t in tickets if t.priority.value.upper() == priority_filter.upper() or t.priority.name.upper() == priority_filter.upper()]
    if user_id_filter:
        tickets = [t for t in tickets if (t.createdBy and t.createdBy.userId == user_id_filter) or (t.assignedTo and t.assignedTo.userId == user_id_filter)]

    return jsonify([t.to_dict() for t in tickets]), 200

# Recuperer les details d'un seul ticket
@app.route("/api/tickets/<int:ticket_id>", methods=["GET"])
def get_ticket(ticket_id: int):
    ticket = gestionnaire.trouverParId(ticket_id)
    if not ticket:
        return jsonify({"error": f"Ticket #{ticket_id} introuvable."}), 404
    return jsonify(ticket.to_dict()), 200

# Creer un nouveau ticket
@app.route("/api/tickets", methods=["POST"])
def create_ticket():
    title = None
    priority_str = "NORMALE"
    user_id = None
    texte_desc = None
    image_path = None

    # Verification si le client envoie du JSON ou du multipart/form-data
    if request.is_json:
        data = request.get_json() or {}
        title = data.get("title")
        priority_str = data.get("priority", "NORMALE")
        user_id = data.get("user_id")
        texte_desc = data.get("description_texte")
        image_path = data.get("description_image")
    else:
        title = request.form.get("title")
        priority_str = request.form.get("priority", "NORMALE")
        user_id = request.form.get("user_id", type=int)
        texte_desc = request.form.get("description_texte")

        # Fichier image uploade
        if "image" in request.files:
            file = request.files["image"]
            if file and file.filename != "":
                filename = f"upload_{date.today().strftime('%Y%m%d')}_{file.filename}"
                saved_path = os.path.join(IMAGES_DIR, filename)
                file.save(saved_path)
                image_path = saved_path
        elif request.form.get("description_image"):
            image_path = request.form.get("description_image")

    if not title:
        return jsonify({"error": "Le titre du ticket est obligatoire."}), 400

    # Conversion de la priorite
    try:
        prio = Priorite(priority_str.upper())
    except (ValueError, KeyError):
        prio = Priorite.NORMALE

    ticket = Ticket(title=title, priority=prio)

    # Ajout de la description texte
    if texte_desc:
        desc_t = DescriptionFactory.createDescription(TypeDescription.TEXTE, texte_desc)
        ticket.addDescription(desc_t)

    # Ajout de la description image
    if image_path:
        desc_i = DescriptionFactory.createDescription(TypeDescription.IMAGE, image_path)
        ticket.addDescription(desc_i)

    # Association au createur
    createur = None
    if user_id:
        createur = trouver_user_par_id(user_id)

    if not createur:
        createur = utilisateurs_list[0] if utilisateurs_list else User("Anonyme", "anon@uqac.ca")

    createur.createTicket(ticket)
    gestionnaire.ajouter(ticket)

    return jsonify(ticket.to_dict()), 201

# Changer le statut d'un ticket
@app.route("/api/tickets/<int:ticket_id>/status", methods=["PUT"])
def update_ticket_status(ticket_id: int):
    ticket = gestionnaire.trouverParId(ticket_id)
    if not ticket:
        return jsonify({"error": f"Ticket #{ticket_id} introuvable."}), 404

    data = request.get_json() or {}
    new_status_str = data.get("status")
    if not new_status_str:
        return jsonify({"error": "Le champ 'status' est requis."}), 400

    trouve = False
    for s in Statut:
        if s.name.upper() == new_status_str.upper() or s.value.upper() == new_status_str.upper():
            ticket.updateStatus(s)
            trouve = True
            break

    if not trouve:
        return jsonify({"error": f"Statut '{new_status_str}' invalide."}), 400

    return jsonify(ticket.to_dict()), 200

# Assigner un ticket a un developpeur
@app.route("/api/tickets/<int:ticket_id>/assign", methods=["PUT"])
def assign_ticket(ticket_id: int):
    ticket = gestionnaire.trouverParId(ticket_id)
    if not ticket:
        return jsonify({"error": f"Ticket #{ticket_id} introuvable."}), 404

    data = request.get_json() or {}
    dev_id = data.get("dev_id")
    dev_name = data.get("dev_name")

    dev_cible = None
    if dev_id:
        dev_cible = trouver_dev_par_id(dev_id)
    elif dev_name:
        for d in developpeurs_list:
            if d.name.lower() == dev_name.lower():
                dev_cible = d
                break

    if not dev_cible:
        return jsonify({"error": "Developpeur introuvable."}), 404

    ticket.assignTo(dev_cible)
    return jsonify(ticket.to_dict()), 200

# Gestion des utilisateurs
@app.route("/api/users", methods=["GET"])
def get_users():
    return jsonify([u.to_dict() for u in utilisateurs_list]), 200

@app.route("/api/users", methods=["POST"])
def create_user():
    data = request.get_json() or {}
    name = data.get("name")
    email = data.get("email")

    if not name or not email:
        return jsonify({"error": "Nom et email obligatoires."}), 400

    nouveau_user = User(name, email)
    utilisateurs_list.append(nouveau_user)
    return jsonify(nouveau_user.to_dict()), 201

# Gestion des developpeurs
@app.route("/api/developpeurs", methods=["GET"])
def get_developpeurs():
    return jsonify([d.to_dict() for d in developpeurs_list]), 200

@app.route("/api/developpeurs", methods=["POST"])
def create_developpeur():
    data = request.get_json() or {}
    name = data.get("name")
    email = data.get("email")

    if not name or not email:
        return jsonify({"error": "Nom et email obligatoires."}), 400

    nouveau_dev = Developpeur(name, email)
    developpeurs_list.append(nouveau_dev)
    return jsonify(nouveau_dev.to_dict()), 201

# Service pour afficher ou telecharger les images
@app.route("/api/images/<path:filename>", methods=["GET"])
def get_image(filename):
    return send_from_directory(IMAGES_DIR, filename)

# Interface web bonus (templates/index.html)
@app.route("/", methods=["GET"])
@app.route("/web", methods=["GET"])
def web_interface():
    return render_template("index.html")

# Lancement direct du serveur
def start_server(port=5000, debug=False):
    app.run(host="0.0.0.0", port=port, debug=debug)

if __name__ == "__main__":
    print("Demarrage du serveur REST...")
    print("API : http://127.0.0.1:5000/api/tickets")
    print("Web (bonus) : http://127.0.0.1:5000/web")
    start_server(port=5000, debug=True)
