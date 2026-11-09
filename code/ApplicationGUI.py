import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk

# Client pour communiquer avec l'API REST
from ApiClient import ApiClient

# Interface graphique Tkinter connectee a l'API REST
class ApplicationGUI:
    def __init__(self, fenetre, api_client: ApiClient = None, gestionnaire=None, utilisateurs=None, developpeurs=None):
        self.fenetre = fenetre
        self.api_client = api_client or ApiClient()

        # Personne actuellement connectee
        self.personne_connectee = None
        self.tickets_caches = []
        self.utilisateurs_caches = []
        self.developpeurs_caches = []

        self.fenetre.title("Gestion des Tickets - Architecture REST (Lab 4)")
        self.fenetre.geometry("740x560")

        # Verifier si l'API repond
        if not self.api_client.test_connection():
            messagebox.showwarning(
                "Attention",
                "Le serveur REST (http://127.0.0.1:5000) semble hors-ligne.\nAssurez-vous que api_server.py est demarre."
            )

        # Construction des deux ecrans
        self.creer_ecran_connexion()
        self.creer_ecran_principal()

        # Affichage initial
        self.afficher_connexion()

#----------------------------------------------------------------------
# 1. ECRAN DE CONNEXION (UTILISATEUR VS DEVELOPPEUR)
#----------------------------------------------------------------------
    def creer_ecran_connexion(self):
        self.cadre_connexion = tk.Frame(self.fenetre, padx=20, pady=20)

        # Titre
        tk.Label(
            self.cadre_connexion,
            text="Gestionnaire de Tickets (Architecture REST)",
            font=("Arial", 14, "bold"),
            fg="#2c3e50"
        ).pack(pady=(5, 5))

        tk.Label(
            self.cadre_connexion,
            text="Connexion a l'API : http://127.0.0.1:5000/api",
            font=("Arial", 9, "italic"),
            fg="#7f8c8d"
        ).pack(pady=(0, 15))

        # Cadre du formulaire
        cadre_form = tk.LabelFrame(self.cadre_connexion, text=" Connexion ", font=("Arial", 11, "bold"), padx=25, pady=20)
        cadre_form.pack(pady=10)

        # Choix du role
        tk.Label(cadre_form, text="Vous etes :", font=("Arial", 11, "bold")).pack(anchor="w", pady=(0, 5))

        self.choix_role = tk.StringVar(value="Utilisateur")

        frame_radios = tk.Frame(cadre_form)
        frame_radios.pack(anchor="w", pady=5)

        radio_user = tk.Radiobutton(
            frame_radios,
            text="Utilisateur",
            variable=self.choix_role,
            value="Utilisateur",
            font=("Arial", 10),
            command=self.changer_type_connexion
        )
        radio_user.pack(side="left", padx=(0, 20))

        radio_dev = tk.Radiobutton(
            frame_radios,
            text="Developpeur",
            variable=self.choix_role,
            value="Developpeur",
            font=("Arial", 10),
            command=self.changer_type_connexion
        )
        radio_dev.pack(side="left")

        # Choix du compte dans la liste recuperee de l'API
        self.label_choix_nom = tk.Label(cadre_form, text="Selectionnez votre compte :", font=("Arial", 10))
        self.label_choix_nom.pack(anchor="w", pady=(15, 5))

        self.combo_comptes = ttk.Combobox(cadre_form, state="readonly", width=40, font=("Arial", 10))
        self.combo_comptes.pack(fill="x", pady=5)

        # Boutons d'action
        frame_boutons = tk.Frame(cadre_form)
        frame_boutons.pack(pady=(20, 5))

        btn_connecter = tk.Button(
            frame_boutons,
            text="Se connecter",
            font=("Arial", 11, "bold"),
            bg="#2ecc71",
            fg="white",
            padx=15,
            pady=5,
            command=self.valider_connexion
        )
        btn_connecter.pack(side="left", padx=5)

        btn_nouveau_compte = tk.Button(
            frame_boutons,
            text="Creer un compte",
            font=("Arial", 10),
            bg="#3498db",
            fg="white",
            padx=12,
            pady=6,
            command=self.ouvrir_fenetre_nouveau_compte
        )
        btn_nouveau_compte.pack(side="left", padx=5)

        # Remplir la liste au demarrage
        self.changer_type_connexion()

    # Mettre a jour la liste des comptes selon le role choisi
    def changer_type_connexion(self):
        role = self.choix_role.get()
        try:
            if role == "Utilisateur":
                self.label_choix_nom.config(text="Selectionnez votre compte Utilisateur :")
                self.utilisateurs_caches = self.api_client.get_users()
                noms = [f"#{u['userId']} - {u['name']} ({u['email']})" for u in self.utilisateurs_caches]
            else:
                self.label_choix_nom.config(text="Selectionnez votre compte Developpeur :")
                self.developpeurs_caches = self.api_client.get_developpeurs()
                noms = [f"#{d['userId']} - {d['name']} ({d['email']})" for d in self.developpeurs_caches]

            self.combo_comptes["values"] = noms
            if noms:
                self.combo_comptes.current(0)
            else:
                self.combo_comptes.set("")
        except Exception as e:
            self.combo_comptes["values"] = []
            messagebox.showerror("Erreur API", f"Impossible de charger les comptes : {e}", parent=self.fenetre)

    # Fenetre de creation d'un compte
    def ouvrir_fenetre_nouveau_compte(self):
        fenetre_compte = tk.Toplevel(self.fenetre)
        fenetre_compte.title("Creer un nouveau compte")
        fenetre_compte.geometry("400x320")

        tk.Label(fenetre_compte, text="Creation d'un Nouveau Compte", font=("Arial", 12, "bold"), fg="#2c3e50").pack(pady=12)

        tk.Label(fenetre_compte, text="Type de compte :", font=("Arial", 10, "bold")).pack(anchor="w", padx=25, pady=(5, 2))
        type_nouveau = tk.StringVar(value="Utilisateur")

        frame_type = tk.Frame(fenetre_compte)
        frame_type.pack(anchor="w", padx=25, pady=2)
        tk.Radiobutton(frame_type, text="Utilisateur", variable=type_nouveau, value="Utilisateur", font=("Arial", 10)).pack(side="left", padx=(0, 15))
        tk.Radiobutton(frame_type, text="Developpeur", variable=type_nouveau, value="Developpeur", font=("Arial", 10)).pack(side="left")

        tk.Label(fenetre_compte, text="Nom complet :", font=("Arial", 10, "bold")).pack(anchor="w", padx=25, pady=(10, 2))
        entree_nom = tk.Entry(fenetre_compte, font=("Arial", 10), width=35)
        entree_nom.pack(padx=25, pady=2)

        tk.Label(fenetre_compte, text="Adresse courriel :", font=("Arial", 10, "bold")).pack(anchor="w", padx=25, pady=(10, 2))
        entree_email = tk.Entry(fenetre_compte, font=("Arial", 10), width=35)
        entree_email.pack(padx=25, pady=2)

        def enregistrer_compte():
            nom = entree_nom.get().strip()
            email = entree_email.get().strip()

            if not nom or not email:
                messagebox.showwarning("Erreur", "Veuillez renseigner le nom et le courriel.", parent=fenetre_compte)
                return

            try:
                if type_nouveau.get() == "Utilisateur":
                    nouveau = self.api_client.create_user(nom, email)
                    self.choix_role.set("Utilisateur")
                else:
                    nouveau = self.api_client.create_developpeur(nom, email)
                    self.choix_role.set("Developpeur")

                self.changer_type_connexion()
                self.combo_comptes.set(f"#{nouveau['userId']} - {nom} ({email})")
                messagebox.showinfo("Succes", f"Compte de {nom} cree avec succes !", parent=fenetre_compte)
                fenetre_compte.destroy()
            except Exception as e:
                messagebox.showerror("Erreur API", f"Echec de creation : {e}", parent=fenetre_compte)

        btn_enregistrer = tk.Button(
            fenetre_compte,
            text="Enregistrer",
            font=("Arial", 10, "bold"),
            bg="#27ae60",
            fg="white",
            padx=10,
            pady=5,
            command=enregistrer_compte
        )
        btn_enregistrer.pack(pady=20)

    # Valider la connexion et passer a l'espace de travail
    def valider_connexion(self):
        index = self.combo_comptes.current()
        if index < 0:
            messagebox.showwarning("Attention", "Veuillez selectionner un compte.", parent=self.fenetre)
            return

        role = self.choix_role.get()
        if role == "Utilisateur":
            self.personne_connectee = self.utilisateurs_caches[index]
            self.personne_connectee["role"] = "Utilisateur"
        else:
            self.personne_connectee = self.developpeurs_caches[index]
            self.personne_connectee["role"] = "Developpeur"

        self.cadre_connexion.pack_forget()
        self.afficher_espace_principal()

#----------------------------------------------------------------------
# 2. ESPACE PRINCIPAL
#----------------------------------------------------------------------
    def creer_ecran_principal(self):
        self.cadre_principal = tk.Frame(self.fenetre)

        # Bandeau superieur avec infos de connexion
        self.cadre_haut = tk.Frame(self.cadre_principal, bg="#34495e", padx=15, pady=8)
        self.cadre_haut.pack(fill="x")

        self.label_info_user = tk.Label(self.cadre_haut, text="", font=("Arial", 11, "bold"), fg="white", bg="#34495e")
        self.label_info_user.pack(side="left")

        btn_deconnexion = tk.Button(
            self.cadre_haut,
            text="Deconnexion",
            font=("Arial", 9),
            bg="#e74c3c",
            fg="white",
            command=self.deconnexion
        )
        btn_deconnexion.pack(side="right")

        # Liste des tickets
        cadre_liste = tk.LabelFrame(self.cadre_principal, text=" Liste des tickets (API REST) ", font=("Arial", 10, "bold"), padx=10, pady=10)
        cadre_liste.pack(fill="both", expand=True, padx=15, pady=10)

        # Filtre par statut
        frame_filtre = tk.Frame(cadre_liste)
        frame_filtre.pack(fill="x", pady=(0, 8))
        tk.Label(frame_filtre, text="Filtrer par statut :", font=("Arial", 9)).pack(side="left", padx=(0, 5))
        self.combo_filtre_statut = ttk.Combobox(frame_filtre, values=["TOUS", "OUVERT", "ASSIGNE", "VALIDATION", "TERMINE"], state="readonly", width=15)
        self.combo_filtre_statut.set("TOUS")
        self.combo_filtre_statut.pack(side="left")
        self.combo_filtre_statut.bind("<<ComboboxSelected>>", lambda e: self.actualiser_liste())

        self.liste_tickets = tk.Listbox(cadre_liste, font=("Arial", 10), height=11, selectmode=tk.SINGLE)
        self.liste_tickets.pack(fill="both", expand=True)

        # Barre de boutons du bas
        self.cadre_boutons = tk.Frame(self.cadre_principal, padx=10, pady=10)
        self.cadre_boutons.pack(fill="x")

        self.btn_nouveau = tk.Button(
            self.cadre_boutons,
            text="Creer un ticket",
            font=("Arial", 10, "bold"),
            bg="#27ae60",
            fg="white",
            command=self.ouvrir_fenetre_creation
        )
        self.btn_voir = tk.Button(
            self.cadre_boutons,
            text="Voir / Visualiser",
            font=("Arial", 10, "bold"),
            bg="#2980b9",
            fg="white",
            command=self.ouvrir_fenetre_visualisation
        )
        self.btn_assigner = tk.Button(self.cadre_boutons, text="Assigner", font=("Arial", 10), command=self.assigner_ticket)
        self.btn_valider = tk.Button(self.cadre_boutons, text="Valider", font=("Arial", 10), command=self.valider_ticket)
        self.btn_fermer = tk.Button(self.cadre_boutons, text="Fermer", font=("Arial", 10), command=self.fermer_ticket)
        self.btn_refresh = tk.Button(self.cadre_boutons, text="Actualiser", font=("Arial", 10), command=self.actualiser_liste)

    # Afficher l'espace principal selon le role
    def afficher_espace_principal(self):
        role_texte = self.personne_connectee.get("role", "Utilisateur")
        nom = self.personne_connectee.get("name", "Inconnu")
        self.label_info_user.config(text=f"Connecte : {nom}  [{role_texte}]")

        for widget in self.cadre_boutons.winfo_children():
            widget.pack_forget()

        if role_texte == "Utilisateur":
            self.btn_nouveau.pack(side="left", padx=5)
            self.btn_voir.pack(side="left", padx=5)
        else:
            self.btn_voir.pack(side="left", padx=5)
            self.btn_assigner.pack(side="left", padx=5)
            self.btn_valider.pack(side="left", padx=5)
            self.btn_fermer.pack(side="left", padx=5)

        self.btn_refresh.pack(side="right", padx=5)
        self.cadre_principal.pack(fill="both", expand=True)
        self.actualiser_liste()

    # Revenir a l'ecran de connexion
    def deconnexion(self):
        self.cadre_principal.pack_forget()
        self.personne_connectee = None
        self.afficher_connexion()

    def afficher_connexion(self):
        self.cadre_connexion.pack(fill="both", expand=True)

#----------------------------------------------------------------------
# 3. ACTUALISATION DES DONNEES VIA L'API
#----------------------------------------------------------------------
    def actualiser_liste(self):
        try:
            statut_filtre = self.combo_filtre_statut.get()
            filtre = None if statut_filtre == "TOUS" else statut_filtre
            self.tickets_caches = self.api_client.get_tickets(status=filtre)

            self.liste_tickets.delete(0, tk.END)
            for t in self.tickets_caches:
                assigne = t["assignedTo"]["name"] if t.get("assignedTo") else "Non assigne"
                self.liste_tickets.insert(
                    tk.END,
                    f"#{t['ticketId']} - {t['title']}  [{t['status']}]  (Priorite: {t['priority']}, Assigne a: {assigne})"
                )
        except Exception as e:
            messagebox.showerror("Erreur API", f"Impossible d'actualiser les tickets : {e}", parent=self.fenetre)

    def get_ticket_selectionne(self):
        selection = self.liste_tickets.curselection()
        if not selection:
            messagebox.showwarning("Attention", "Veuillez selectionner un ticket.")
            return None
        return self.tickets_caches[selection[0]]

#----------------------------------------------------------------------
# 4. CREATION D'UN TICKET
#----------------------------------------------------------------------
    def ouvrir_fenetre_creation(self):
        fenetre_crea = tk.Toplevel(self.fenetre)
        fenetre_crea.title("Creer un nouveau ticket")
        fenetre_crea.geometry("460x490")

        chemin_image_choisie = tk.StringVar(value="")

        tk.Label(fenetre_crea, text="Titre du ticket :", font=("Arial", 10, "bold")).pack(anchor="w", padx=15, pady=(10, 2))
        entree_titre = tk.Entry(fenetre_crea, font=("Arial", 10), width=45)
        entree_titre.pack(padx=15, pady=5)

        tk.Label(fenetre_crea, text="Priorite :", font=("Arial", 10, "bold")).pack(anchor="w", padx=15, pady=(10, 2))
        combo_priorite = ttk.Combobox(fenetre_crea, values=["BASSE", "NORMALE", "HAUTE"], state="readonly", width=20)
        combo_priorite.set("NORMALE")
        combo_priorite.pack(anchor="w", padx=15, pady=5)

        tk.Label(fenetre_crea, text="Description en format texte :", font=("Arial", 10, "bold")).pack(anchor="w", padx=15, pady=(10, 2))
        zone_texte = tk.Text(fenetre_crea, height=5, width=45, font=("Arial", 10))
        zone_texte.pack(padx=15, pady=5)

        tk.Label(fenetre_crea, text="Description en format image (optionnel) :", font=("Arial", 10, "bold")).pack(anchor="w", padx=15, pady=(10, 2))

        def choisir_image():
            chemin = filedialog.askopenfilename(
                parent=fenetre_crea,
                title="Choisir une image",
                filetypes=[("Images", "*.png;*.jpg;*.jpeg;*.gif;*.bmp"), ("Tous les fichiers", "*.*")]
            )
            if chemin:
                chemin_image_choisie.set(chemin)
                label_image_path.config(text=f"Fichier : {os.path.basename(chemin)}", fg="green")

        bouton_parcourir = tk.Button(fenetre_crea, text="Parcourir une image...", command=choisir_image)
        bouton_parcourir.pack(anchor="w", padx=15, pady=2)

        label_image_path = tk.Label(fenetre_crea, text="Aucune image selectionnee", font=("Arial", 9, "italic"), fg="gray")
        label_image_path.pack(anchor="w", padx=15, pady=2)

        def enregistrer_ticket():
            titre = entree_titre.get().strip()
            texte = zone_texte.get("1.0", tk.END).strip()
            img_path = chemin_image_choisie.get()

            if not titre:
                messagebox.showwarning("Erreur", "Veuillez entrer un titre.", parent=fenetre_crea)
                return

            if not texte and not img_path:
                messagebox.showwarning("Erreur", "Veuillez entrer au moins du texte ou une image.", parent=fenetre_crea)
                return

            try:
                prio = combo_priorite.get()
                user_id = self.personne_connectee.get("userId", 1)

                ticket_cree = self.api_client.create_ticket(
                    title=titre,
                    priority=prio,
                    user_id=user_id,
                    description_texte=texte if texte else None,
                    image_path=img_path if img_path else None
                )

                messagebox.showinfo("Succes", f"Ticket #{ticket_cree['ticketId']} cree avec succes !", parent=fenetre_crea)
                self.actualiser_liste()
                fenetre_crea.destroy()
            except Exception as e:
                messagebox.showerror("Erreur API", f"Echec de creation : {e}", parent=fenetre_crea)

        bouton_valider = tk.Button(
            fenetre_crea,
            text="Creer le ticket",
            font=("Arial", 11, "bold"),
            bg="#27ae60",
            fg="white",
            command=enregistrer_ticket
        )
        bouton_valider.pack(pady=15)

#----------------------------------------------------------------------
# 5. VISUALISATION DES DETAILS DU TICKET
#----------------------------------------------------------------------
    def ouvrir_fenetre_visualisation(self):
        ticket_sommaire = self.get_ticket_selectionne()
        if not ticket_sommaire:
            return

        try:
            ticket = self.api_client.get_ticket(ticket_sommaire["ticketId"])
        except Exception as e:
            messagebox.showerror("Erreur API", f"Impossible de charger le ticket : {e}")
            return

        fenetre_details = tk.Toplevel(self.fenetre)
        fenetre_details.title(f"Details du Ticket #{ticket['ticketId']}")
        fenetre_details.geometry("520x600")

        tk.Label(fenetre_details, text=f"Ticket #{ticket['ticketId']} : {ticket['title']}", font=("Arial", 12, "bold")).pack(pady=(10, 5))

        assigne = ticket["assignedTo"]["name"] if ticket.get("assignedTo") else "Non assigne"
        createur = ticket["createdBy"]["name"] if ticket.get("createdBy") else "Inconnu"
        info = f"Statut : {ticket['status']}   |   Priorite : {ticket['priority']}\nCree par : {createur}   |   Assigne a : {assigne}\nCreation : {ticket['creationDate']}   |   Mise a jour : {ticket['updateDate']}"
        tk.Label(fenetre_details, text=info, font=("Arial", 9), justify="center").pack(pady=5)

        ttk.Separator(fenetre_details, orient="horizontal").pack(fill="x", padx=15, pady=8)

        # Visualisation texte
        tk.Label(fenetre_details, text="Description Texte :", font=("Arial", 10, "bold")).pack(anchor="w", padx=15, pady=2)
        textes = [d.get("contenu") or d.get("chemin") for d in ticket.get("descriptions", []) if d.get("type") == "TEXTE"]
        zone_texte = tk.Text(fenetre_details, height=4, width=55, font=("Arial", 10))
        zone_texte.pack(padx=15, pady=5)
        if textes:
            zone_texte.insert(tk.END, "\n".join(textes))
        else:
            zone_texte.insert(tk.END, "(Aucune description textuelle pour ce ticket)")
        zone_texte.config(state="disabled")

        # Visualisation image
        tk.Label(fenetre_details, text="Description Image :", font=("Arial", 10, "bold")).pack(anchor="w", padx=15, pady=(10, 2))
        images = [d.get("chemin") for d in ticket.get("descriptions", []) if d.get("type") == "IMAGE"]

        if images and os.path.exists(images[0]):
            try:
                img_pil = Image.open(images[0])
                img_pil = img_pil.resize((320, 190))
                photo = ImageTk.PhotoImage(img_pil)

                lbl_image = tk.Label(fenetre_details, image=photo, relief="groove")
                lbl_image.image = photo
                lbl_image.pack(pady=5)
                tk.Label(fenetre_details, text=f"Fichier : {os.path.basename(images[0])}", font=("Arial", 8, "italic"), fg="gray").pack()
            except Exception as e:
                tk.Label(fenetre_details, text=f"Erreur d'affichage : {e}", fg="red").pack()
        else:
            tk.Label(fenetre_details, text="(Aucune image jointe pour ce ticket)", font=("Arial", 10, "italic"), fg="gray").pack(pady=15)

        bouton_fermer = tk.Button(fenetre_details, text="Fermer", width=15, command=fenetre_details.destroy)
        bouton_fermer.pack(pady=15)

#----------------------------------------------------------------------
# 6. ACTIONS DU DEVELOPPEUR
#----------------------------------------------------------------------
    def assigner_ticket(self):
        ticket = self.get_ticket_selectionne()
        if not ticket:
            return

        try:
            devs = self.api_client.get_developpeurs()
        except Exception as e:
            messagebox.showerror("Erreur API", f"Impossible de charger les developpeurs : {e}")
            return

        if not devs:
            messagebox.showwarning("Attention", "Aucun developpeur enregistre.")
            return

        fenetre_assign = tk.Toplevel(self.fenetre)
        fenetre_assign.title("Assigner le ticket")
        fenetre_assign.geometry("360x180")

        tk.Label(fenetre_assign, text=f"Assigner le Ticket #{ticket['ticketId']} :", font=("Arial", 10, "bold")).pack(pady=10)

        noms_devs = [f"#{d['userId']} - {d['name']}" for d in devs]
        combo_devs = ttk.Combobox(fenetre_assign, values=noms_devs, state="readonly", width=30)
        combo_devs.set(noms_devs[0])
        combo_devs.pack(pady=5)

        def confirmer_assignation():
            index = combo_devs.current()
            if index < 0:
                return
            dev_cible = devs[index]
            try:
                self.api_client.assign_ticket(ticket["ticketId"], dev_id=dev_cible["userId"])
                messagebox.showinfo("Succes", f"Ticket #{ticket['ticketId']} assigne a {dev_cible['name']} !", parent=fenetre_assign)
                self.actualiser_liste()
                fenetre_assign.destroy()
            except Exception as e:
                messagebox.showerror("Erreur API", f"Echec d'assignation : {e}", parent=fenetre_assign)

        tk.Button(fenetre_assign, text="Confirmer l'assignation", bg="#2980b9", fg="white", command=confirmer_assignation).pack(pady=15)

    def valider_ticket(self):
        ticket = self.get_ticket_selectionne()
        if not ticket:
            return

        try:
            self.api_client.update_ticket_status(ticket["ticketId"], "VALIDATION")
            messagebox.showinfo("Succes", f"Ticket #{ticket['ticketId']} passe en statut VALIDATION.")
            self.actualiser_liste()
        except Exception as e:
            messagebox.showerror("Erreur API", f"Echec de la validation : {e}")

    def fermer_ticket(self):
        ticket = self.get_ticket_selectionne()
        if not ticket:
            return

        try:
            self.api_client.update_ticket_status(ticket["ticketId"], "TERMINÉ")
            messagebox.showinfo("Succes", f"Ticket #{ticket['ticketId']} ferme (statut TERMINE).")
            self.actualiser_liste()
        except Exception as e:
            messagebox.showerror("Erreur API", f"Echec de la fermeture : {e}")
