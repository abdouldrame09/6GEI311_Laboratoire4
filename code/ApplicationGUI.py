import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk

#Importation des classes metier 
from Statut import Statut
from Priorite import Priorite
from TypeDescription import TypeDescription
from DescriptionFactory import DescriptionFactory
from Ticket import Ticket
from User import User
from Developpeur import Developpeur
from TextObject import TextObject
from ImageObject import ImageObject

#Client pour communiquer avec l'API REST
from ApiClient import ApiClient

#Classe pour l'interface graphique Tkinter
class ApplicationGUI:
    def __init__(self, fenetre, gestionnaire=None, utilisateurs=None, developpeurs=None, api_client: ApiClient = None):
        self.fenetre = fenetre
        self.api_client = api_client or ApiClient()
        self.gestionnaire = gestionnaire
        self.utilisateurs = utilisateurs or []
        self.developpeurs = developpeurs or []

        #Personne actuellement connectee
        self.personne_connectee = None
        self.tickets_caches = []
        self.utilisateurs_caches = []
        self.developpeurs_caches = []

        self.fenetre.title("Gestion des Tickets - UQAC (Lab 4)")
        self.fenetre.geometry("700x530")

        #Construction des deux ecrans (connexion et espace principal)
        self.creer_ecran_connexion()
        self.creer_ecran_principal()

        #Au depart, on affiche l'ecran de connexion
        self.afficher_connexion()

#----------------------------------------------------------------------
# 1. ECRAN DE CONNEXION SEPARE (UTILISATEUR VS DEVELOPPEUR)
#----------------------------------------------------------------------
    def creer_ecran_connexion(self):
        self.cadre_connexion = tk.Frame(self.fenetre, padx=20, pady=20)

        #Titre de bienvenue
        tk.Label(self.cadre_connexion, text="Bienvenue dans le Gestionnaire de Tickets", font=("Arial", 14, "bold"), fg="#2c3e50").pack(pady=(10, 20))

        #Cadre avec bordure pour la connexion
        cadre_form = tk.LabelFrame(self.cadre_connexion, text=" Connexion ", font=("Arial", 11, "bold"), padx=25, pady=20)
        cadre_form.pack(pady=10)

        #1. Choix du type de compte (Utilisateur ou Developpeur)
        tk.Label(cadre_form, text="Vous êtes :", font=("Arial", 11, "bold")).pack(anchor="w", pady=(0, 5))

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
            text="Développeur",
            variable=self.choix_role,
            value="Développeur",
            font=("Arial", 10),
            command=self.changer_type_connexion
        )
        radio_dev.pack(side="left")

        #2. Choix du profil dans la liste
        self.label_choix_nom = tk.Label(cadre_form, text="Sélectionnez votre compte Utilisateur :", font=("Arial", 10))
        self.label_choix_nom.pack(anchor="w", pady=(15, 5))

        self.combo_comptes = ttk.Combobox(cadre_form, state="readonly", width=35, font=("Arial", 10))
        self.combo_comptes.pack(fill="x", pady=5)

        #3. Cadre des boutons d'action (Se connecter et Creer un compte)
        frame_boutons_connexion = tk.Frame(cadre_form)
        frame_boutons_connexion.pack(pady=(20, 5))

        btn_connecter = tk.Button(
            frame_boutons_connexion,
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
            frame_boutons_connexion,
            text="Créer un compte",
            font=("Arial", 10),
            bg="#3498db",
            fg="white",
            padx=12,
            pady=6,
            command=self.ouvrir_fenetre_nouveau_compte
        )
        btn_nouveau_compte.pack(side="left", padx=5)

        #Initialiser la liste selon le choix par defaut (Utilisateur)
        self.changer_type_connexion()

#Fonction pour changer la liste des comptes selon le role selectionne
    def changer_type_connexion(self):
        role = self.choix_role.get()
        try:
            if role == "Utilisateur":
                self.label_choix_nom.config(text="Sélectionnez votre compte Utilisateur :")
                self.utilisateurs_caches = self.api_client.get_users()
                noms = [f"{u['name']} ({u['email']})" for u in self.utilisateurs_caches]
            else:
                self.label_choix_nom.config(text="Sélectionnez votre compte Développeur :")
                self.developpeurs_caches = self.api_client.get_developpeurs()
                noms = [f"{d['name']} ({d['email']})" for d in self.developpeurs_caches]

            self.combo_comptes["values"] = noms
            if noms:
                self.combo_comptes.current(0)
            else:
                self.combo_comptes.set("")
        except Exception:
            self.combo_comptes["values"] = []

#Fonction pour creer un nouveau compte (Utilisateur ou Developpeur)
    def ouvrir_fenetre_nouveau_compte(self):
        fenetre_compte = tk.Toplevel(self.fenetre)
        fenetre_compte.title("Créer un nouveau compte")
        fenetre_compte.geometry("400x320")

        tk.Label(fenetre_compte, text="Création d'un Nouveau Compte", font=("Arial", 12, "bold"), fg="#2c3e50").pack(pady=12)

        #Choix du type de compte
        tk.Label(fenetre_compte, text="Type de compte :", font=("Arial", 10, "bold")).pack(anchor="w", padx=25, pady=(5, 2))
        type_nouveau = tk.StringVar(value="Utilisateur")

        frame_type = tk.Frame(fenetre_compte)
        frame_type.pack(anchor="w", padx=25, pady=2)
        tk.Radiobutton(frame_type, text="Utilisateur", variable=type_nouveau, value="Utilisateur", font=("Arial", 10)).pack(side="left", padx=(0, 15))
        tk.Radiobutton(frame_type, text="Développeur", variable=type_nouveau, value="Développeur", font=("Arial", 10)).pack(side="left")

        #Champ Nom
        tk.Label(fenetre_compte, text="Nom complet :", font=("Arial", 10, "bold")).pack(anchor="w", padx=25, pady=(10, 2))
        entree_nom = tk.Entry(fenetre_compte, font=("Arial", 10), width=35)
        entree_nom.pack(padx=25, pady=2)

        #Champ Email
        tk.Label(fenetre_compte, text="Adresse courriel :", font=("Arial", 10, "bold")).pack(anchor="w", padx=25, pady=(10, 2))
        entree_email = tk.Entry(fenetre_compte, font=("Arial", 10), width=35)
        entree_email.pack(padx=25, pady=2)

        #Fonction pour enregistrer le compte
        def enregistrer_compte():
            nom = entree_nom.get().strip()
            email = entree_email.get().strip()

            if not nom or not email:
                messagebox.showwarning("Erreur", "Veuillez renseigner le nom et l'adresse courriel.", parent=fenetre_compte)
                return

            try:
                if type_nouveau.get() == "Utilisateur":
                    self.api_client.create_user(nom, email)
                    self.choix_role.set("Utilisateur")
                else:
                    self.api_client.create_developpeur(nom, email)
                    self.choix_role.set("Développeur")

                self.changer_type_connexion()
                self.combo_comptes.set(f"{nom} ({email})")
                messagebox.showinfo("Succès", f"Le compte de {nom} a été créé avec succès !", parent=fenetre_compte)
                fenetre_compte.destroy()
            except Exception as e:
                messagebox.showerror("Erreur API", f"Impossible d'enregistrer le compte : {e}", parent=fenetre_compte)

        btn_enregistrer = tk.Button(
            fenetre_compte,
            text="Enregistrer le compte",
            font=("Arial", 10, "bold"),
            bg="#27ae60",
            fg="white",
            padx=10,
            pady=5,
            command=enregistrer_compte
        )
        btn_enregistrer.pack(pady=20)

#Fonction pour valider la connexion et passer a l'espace de travail
    def valider_connexion(self):
        index = self.combo_comptes.current()
        if index < 0:
            messagebox.showwarning("Attention", "Veuillez choisir un profil dans la liste.", parent=self.fenetre)
            return

        role = self.choix_role.get()
        if role == "Utilisateur":
            self.personne_connectee = self.utilisateurs_caches[index]
            self.personne_connectee["role"] = "Utilisateur"
        else:
            self.personne_connectee = self.developpeurs_caches[index]
            self.personne_connectee["role"] = "Développeur"

        #Masquer l'ecran de connexion et afficher l'espace principal
        self.cadre_connexion.pack_forget()
        self.afficher_espace_principal()

#----------------------------------------------------------------------
# 2. ESPACE PRINCIPAL 
#----------------------------------------------------------------------
    def creer_ecran_principal(self):
        self.cadre_principal = tk.Frame(self.fenetre)

        #Cadre du haut : Bandeau d'information utilisateur + bouton deconnexion
        self.cadre_haut = tk.Frame(self.cadre_principal, bg="#34495e", padx=15, pady=8)
        self.cadre_haut.pack(fill="x")

        self.label_info_user = tk.Label(self.cadre_haut, text="", font=("Arial", 11, "bold"), fg="white", bg="#34495e")
        self.label_info_user.pack(side="left")

        btn_deconnexion = tk.Button(
            self.cadre_haut,
            text="Changer de rôle / Déconnexion",
            font=("Arial", 9),
            bg="#e74c3c",
            fg="white",
            command=self.deconnexion
        )
        btn_deconnexion.pack(side="right")

        #Cadre du milieu : Liste des tickets
        cadre_liste = tk.LabelFrame(self.cadre_principal, text=" Liste de tous les tickets ", font=("Arial", 10, "bold"), padx=10, pady=10)
        cadre_liste.pack(fill="both", expand=True, padx=15, pady=10)

        self.liste_tickets = tk.Listbox(cadre_liste, font=("Arial", 10), height=10, selectmode=tk.SINGLE)
        self.liste_tickets.pack(fill="both", expand=True)

        #Cadre du bas : Boutons d'action adaptes
        self.cadre_boutons = tk.Frame(self.cadre_principal, padx=10, pady=10)
        self.cadre_boutons.pack(fill="x")

        #Bouton Nouveau Ticket (Visible pour Utilisateur)
        self.btn_nouveau = tk.Button(
            self.cadre_boutons,
            text="Créer un ticket",
            font=("Arial", 10, "bold"),
            bg="#27ae60",
            fg="white",
            command=self.ouvrir_fenetre_creation
        )

        #Bouton Visualiser le ticket (Visible pour tout le monde)
        self.btn_voir = tk.Button(
            self.cadre_boutons,
            text="Voir / Visualiser",
            font=("Arial", 10, "bold"),
            bg="#2980b9",
            fg="white",
            command=self.ouvrir_fenetre_visualisation
        )

        #Boutons reserves aux Developpeurs
        self.btn_assigner = tk.Button(self.cadre_boutons, text="Assigner", font=("Arial", 10), command=self.assigner_ticket)
        self.btn_valider = tk.Button(self.cadre_boutons, text="Valider", font=("Arial", 10), command=self.valider_ticket)
        self.btn_fermer = tk.Button(self.cadre_boutons, text="Fermer", font=("Arial", 10), command=self.fermer_ticket)

        #Bouton actualiser
        self.btn_refresh = tk.Button(self.cadre_boutons, text="Actualiser", font=("Arial", 10), command=self.actualiser_liste)

#Fonction pour afficher l'espace principal et adapter les boutons au role
    def afficher_espace_principal(self):
        #Mise a jour du texte de bienvenue
        role_texte = self.personne_connectee.get("role", "Utilisateur")
        nom = self.personne_connectee.get("name", "Inconnu")
        self.label_info_user.config(text=f"Connecté : {nom}  [{role_texte}]")

        #Nettoyer les boutons affiches
        for widget in self.cadre_boutons.winfo_children():
            widget.pack_forget()

        #Affichage des boutons selon le role
        if role_texte == "Utilisateur":
            #Mode UTILISATEUR : peut creer et visualiser
            self.btn_nouveau.pack(side="left", padx=5)
            self.btn_voir.pack(side="left", padx=5)
        else:
            #Mode DEVELOPPEUR : peut visualiser, assigner, valider, fermer
            self.btn_voir.pack(side="left", padx=5)
            self.btn_assigner.pack(side="left", padx=5)
            self.btn_valider.pack(side="left", padx=5)
            self.btn_fermer.pack(side="left", padx=5)

        self.btn_refresh.pack(side="right", padx=5)

        #Afficher le cadre principal et charger les tickets
        self.cadre_principal.pack(fill="both", expand=True)
        self.actualiser_liste()

#Fonction pour se deconnecter et revenir a l'ecran de connexion
    def deconnexion(self):
        self.cadre_principal.pack_forget()
        self.personne_connectee = None
        self.afficher_connexion()

#Fonction pour afficher l'ecran de connexion
    def afficher_connexion(self):
        self.cadre_connexion.pack(fill="both", expand=True)

#----------------------------------------------------------------------
# 3. GESTION DE LA LISTE DES TICKETS
#----------------------------------------------------------------------
    def actualiser_liste(self):
        try:
            self.tickets_caches = self.api_client.get_tickets()
            self.liste_tickets.delete(0, tk.END)
            for t in self.tickets_caches:
                assigne = t["assignedTo"]["name"] if t.get("assignedTo") else "Non assigné"
                self.liste_tickets.insert(
                    tk.END,
                    f"#{t['ticketId']} - {t['title']}  [{t['status']}]  (Priorité: {t['priority']}, Assigné à: {assigne})"
                )
        except Exception as e:
            messagebox.showerror("Erreur API", f"Impossible d'actualiser la liste des tickets : {e}", parent=self.fenetre)

    def get_ticket_selectionne(self):
        selection = self.liste_tickets.curselection()
        if not selection:
            messagebox.showwarning("Attention", "Veuillez sélectionner un ticket dans la liste.")
            return None
        index = selection[0]
        return self.tickets_caches[index]

#----------------------------------------------------------------------
# 4. FENETRE DE CREATION D'UN TICKET
#----------------------------------------------------------------------
    def ouvrir_fenetre_creation(self):
        fenetre_crea = tk.Toplevel(self.fenetre)
        fenetre_crea.title("Créer un nouveau ticket")
        fenetre_crea.geometry("450x480")

        chemin_image_choisie = tk.StringVar(value="")

        #Champ Titre
        tk.Label(fenetre_crea, text="Titre du ticket :", font=("Arial", 10, "bold")).pack(anchor="w", padx=15, pady=(10, 2))
        entree_titre = tk.Entry(fenetre_crea, font=("Arial", 10), width=45)
        entree_titre.pack(padx=15, pady=5)

        #Champ Priorite
        tk.Label(fenetre_crea, text="Priorité :", font=("Arial", 10, "bold")).pack(anchor="w", padx=15, pady=(10, 2))
        combo_priorite = ttk.Combobox(fenetre_crea, values=["BASSE", "NORMALE", "HAUTE"], state="readonly", width=20)
        combo_priorite.set("NORMALE")
        combo_priorite.pack(anchor="w", padx=15, pady=5)

        #Champ Description texte
        tk.Label(fenetre_crea, text="Description en format texte :", font=("Arial", 10, "bold")).pack(anchor="w", padx=15, pady=(10, 2))
        zone_texte = tk.Text(fenetre_crea, height=5, width=45, font=("Arial", 10))
        zone_texte.pack(padx=15, pady=5)

        #Champ Description image
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

        label_image_path = tk.Label(fenetre_crea, text="Aucune image sélectionnée", font=("Arial", 9, "italic"), fg="gray")
        label_image_path.pack(anchor="w", padx=15, pady=2)

        #Note d'aide
        tk.Label(fenetre_crea, text="* Le ticket peut contenir du texte, une image, ou les deux.", font=("Arial", 8, "italic"), fg="#555").pack(pady=5)

        #Enregistrement du ticket
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

                messagebox.showinfo("Succès", f"Ticket #{ticket_cree['ticketId']} créé avec succès !", parent=fenetre_crea)
                self.actualiser_liste()
                fenetre_crea.destroy()
            except Exception as e:
                messagebox.showerror("Erreur API", f"Impossible de créer le ticket : {e}", parent=fenetre_crea)

        bouton_valider = tk.Button(
            fenetre_crea,
            text="Créer le ticket",
            font=("Arial", 11, "bold"),
            bg="#27ae60",
            fg="white",
            command=enregistrer_ticket
        )
        bouton_valider.pack(pady=15)

#----------------------------------------------------------------------
# 5. FENETRE DE VISUALISATION (TEXTE ET IMAGE)
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
        fenetre_details.title(f"Visualisation du Ticket #{ticket['ticketId']}")
        fenetre_details.geometry("520x600")

        tk.Label(fenetre_details, text=f"Ticket #{ticket['ticketId']} : {ticket['title']}", font=("Arial", 12, "bold")).pack(pady=(10, 5))

        assigne = ticket["assignedTo"]["name"] if ticket.get("assignedTo") else "Non assigné"
        createur = ticket["createdBy"]["name"] if ticket.get("createdBy") else "Inconnu"
        info = f"Statut : {ticket['status']}   |   Priorité : {ticket['priority']}\nCréé par : {createur}   |   Assigné à : {assigne}\nDate : {ticket['creationDate']}"
        tk.Label(fenetre_details, text=info, font=("Arial", 9), justify="center").pack(pady=5)

        ttk.Separator(fenetre_details, orient="horizontal").pack(fill="x", padx=15, pady=8)

        #1. Visualisation texte
        tk.Label(fenetre_details, text="Description Texte :", font=("Arial", 10, "bold")).pack(anchor="w", padx=15, pady=2)

        textes = [d.get("contenu") or d.get("chemin") for d in ticket.get("descriptions", []) if d.get("type") == "TEXTE"]
        zone_texte = tk.Text(fenetre_details, height=4, width=55, font=("Arial", 10))
        zone_texte.pack(padx=15, pady=5)
        if textes:
            zone_texte.insert(tk.END, "\n".join(textes))
        else:
            zone_texte.insert(tk.END, "(Aucune description textuelle pour ce ticket)")
        zone_texte.config(state="disabled")

        #2. Visualisation image
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
# 6. ACTIONS DU DEVELOPPEUR (ASSIGNER, VALIDER, FERMER)
#----------------------------------------------------------------------
    def assigner_ticket(self):
        ticket = self.get_ticket_selectionne()
        if not ticket:
            return

        try:
            devs = self.api_client.get_developpeurs()
        except Exception as e:
            messagebox.showerror("Erreur API", f"Impossible de charger les développeurs : {e}")
            return

        if not devs:
            messagebox.showwarning("Attention", "Aucun développeur enregistré.")
            return

        fenetre_assign = tk.Toplevel(self.fenetre)
        fenetre_assign.title("Assigner le ticket")
        fenetre_assign.geometry("350x180")

        tk.Label(fenetre_assign, text=f"Assigner le Ticket #{ticket['ticketId']} :", font=("Arial", 10, "bold")).pack(pady=10)

        noms_devs = [d["name"] for d in devs]
        combo_devs = ttk.Combobox(fenetre_assign, values=noms_devs, state="readonly", width=25)
        combo_devs.set(noms_devs[0])
        combo_devs.pack(pady=5)

        def confirmer_assignation():
            index = combo_devs.current()
            if index < 0:
                return
            dev_cible = devs[index]
            try:
                self.api_client.assign_ticket(ticket["ticketId"], dev_id=dev_cible["userId"])
                messagebox.showinfo("Succès", f"Ticket #{ticket['ticketId']} assigné à {dev_cible['name']} !", parent=fenetre_assign)
                self.actualiser_liste()
                fenetre_assign.destroy()
            except Exception as e:
                messagebox.showerror("Erreur API", f"Impossible d'assigner le ticket : {e}", parent=fenetre_assign)

        tk.Button(fenetre_assign, text="Confirmer l'assignation", bg="#2980b9", fg="white", command=confirmer_assignation).pack(pady=15)

    def valider_ticket(self):
        ticket = self.get_ticket_selectionne()
        if not ticket:
            return

        try:
            self.api_client.update_ticket_status(ticket["ticketId"], "VALIDATION")
            messagebox.showinfo("Succès", f"Le ticket #{ticket['ticketId']} est maintenant en statut VALIDATION.")
            self.actualiser_liste()
        except Exception as e:
            messagebox.showerror("Erreur API", f"Impossible de valider le ticket : {e}")

    def fermer_ticket(self):
        ticket = self.get_ticket_selectionne()
        if not ticket:
            return

        try:
            self.api_client.update_ticket_status(ticket["ticketId"], "TERMINÉ")
            messagebox.showinfo("Succès", f"Le ticket #{ticket['ticketId']} a été FERMÉ avec le statut TERMINÉ.")
            self.actualiser_liste()
        except Exception as e:
            messagebox.showerror("Erreur API", f"Impossible de fermer le ticket : {e}")
