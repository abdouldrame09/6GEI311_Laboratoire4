# Université du Québec à Chicoutimi (UQAC)
## 6GEI311 — Architecture des logiciels (Automne 2026)

### Rapport de Laboratoire 4 : Intégration logicielle et Architecture REST

**Membres de l'équipe :**
- Dramé, Abdramane (Code permanent : `DRAA04070300`)
- Doumbia, Djan Ibrahim (Code permanent : `DOUD23110200`)

**Délai de remise :** 11 novembre 2026

---

## Section I — Résumé des modifications apportées à la partie métier et la partie UI pour l’Intégration via une interface REST

Dans les laboratoires précédents (Lab 2 et Lab 3), notre système de gestion de tickets fonctionnait en mode local (standalone). L'interface graphique Tkinter manipulait directement les objets Python en mémoire vive et appelait directement les méthodes du `GestionnaireTickets`. Le problème majeur avec cette façon de faire, c'était que l'application était enfermée sur un seul ordinateur : si deux utilisateurs voulaient accéder aux tickets ou travailler en même temps sur des postes différents, c'était impossible car les données n'étaient pas partagées.

Pour ce laboratoire 4, on a donc transformé notre code pour passer à une architecture distribuée client-serveur basée sur une API REST, en appliquant le patron de conception MVC (Modèle - Vue - Contrôleur).

Lors de la conception de notre programme, on a apporté des modifications ciblées à la fois sur la partie métier, sur le contrôleur et sur l'interface graphique :

### 1. Modifications au niveau de la partie métier (Le Modèle)
D'abord, pour la transmission des données sur le réseau, le problème était qu'un objet Python (`Ticket`, `User`, `ImageObject`, etc.) ne peut pas être envoyé directement tel quel à travers une requête HTTP. Pour résoudre ce problème, nous avons ajouté une méthode `to_dict()` dans chacune de nos classes métier (`Ticket.py`, `User.py`, `Developpeur.py`, `DescriptionTicket.py`, `TextObject.py`, `ImageObject.py`). Cette méthode transforme les attributs de l'objet en un dictionnaire clé-valeur standard, ce qui permet ensuite à Flask de le convertir automatiquement en format JSON avec `jsonify()`.

Ensuite, au niveau de la logique métier pure, on a conservé tout ce qui avait été développé au Lab 2 et au Lab 3 : la vérification des rôles, l'assignation des tickets à un développeur, le changement des statuts (`VALIDATION`, `TERMINE`) et la classe `DescriptionFactory` pour créer les descriptions texte et image. Le grand changement ici, c'est que la couche métier a été complètement isolée de Tkinter. Elle vit maintenant uniquement sur le serveur dans `api_server.py`, ce qui garantit qu'il n'y a qu'une seule source de vérité pour tous les utilisateurs.

### 2. Conception du Contrôleur (L'API REST avec Flask)
Pour relier notre modèle métier aux interfaces graphiques, nous avons créé un serveur avec le framework Flask (`api_server.py`). Ce fichier joue le rôle de contrôleur dans le patron MVC. On y a défini l'ensemble des routes REST dont l'application a besoin pour fonctionner :

- **`GET /api/tickets`** : Permet de récupérer la liste de tous les tickets enregistrés sur le serveur. On a aussi ajouté la possibilité de filtrer par statut (`?status=...`) ou par priorité (`?priority=...`).
- **`GET /api/tickets/<id>`** : Permet de récupérer les informations détaillées d'un ticket spécifique quand on clique dessus.
- **`POST /api/tickets`** : Permet de créer un nouveau ticket. Le problème qu'on avait ici, c'est qu'un ticket peut contenir à la fois du texte et un fichier image. Pour résoudre ce problème, la route accepte soit du JSON simple pour le texte, soit du format `multipart/form-data` quand une image est sélectionnée, ce qui permet d'enregistrer physiquement le fichier dans le dossier `images/` du serveur.
- **`PUT /api/tickets/<id>/assign`** : Permet d'assigner un ticket à un développeur choisi dans la liste. Le ticket passe alors automatiquement au statut `ASSIGNE`.
- **`PUT /api/tickets/<id>/status`** : Permet de modifier le statut d'un ticket pour le faire passer à `VALIDATION` ou le fermer en `TERMINE`.
- **`GET` et `POST` sur `/api/users` et `/api/developpeurs`** : Permettent de récupérer les listes de comptes et d'en créer de nouveaux.
- **`GET /api/images/<nom>`** : Permet au serveur de distribuer les images enregistrées pour que les clients puissent les afficher.

### 3. Modifications au niveau de l'interface graphique (La Vue)
Au niveau de l'interface graphique Tkinter (`ApplicationGUI.py`), le problème était qu'au Lab 3, l'interface appelait directement `self.gestionnaire.ajouter(ticket)` ou modifiait les attributs des objets en mémoire locale. Pour intégrer l'API REST sans mélanger le code d'affichage avec les requêtes réseau, nous avons créé une classe intermédiaire `ApiClient.py` qui utilise la bibliothèque `requests`.

Désormais, dès que l'utilisateur clique sur un bouton dans la fenêtre Tkinter (par exemple se connecter, créer un ticket, assigner ou valider), l'interface n'interagit plus avec la mémoire :
1. `ApplicationGUI.py` appelle une méthode de `ApiClient.py`.
2. `ApiClient` envoie la requête HTTP appropriée (`GET`, `POST` ou `PUT`) à l'adresse `http://127.0.0.1:5000/api`.
3. Le serveur Flask traite la demande, met à jour le modèle métier et renvoie la réponse au format JSON.
4. L'interface Tkinter reçoit les données à jour et rafraîchit immédiatement son affichage (par exemple avec `actualiser_liste()`).

Enfin, pour faciliter le lancement du projet lors de la démonstration, on a créé un script `main.py` qui utilise un thread pour démarrer automatiquement le serveur Flask en arrière-plan, puis lance la fenêtre Tkinter.

### 4. Interface Web simple (Bonus)
Pour réaliser le bonus demandé dans l'énoncé et démontrer l'intégration de l'API, nous avons créé une interface web simple située dans `templates/index.html` et accessible sur `http://127.0.0.1:5000/web`. Cette page web utilise du code JavaScript natif (`fetch()`) pour appeler exactement la même API REST que celle utilisée par Tkinter. Cela prouve bien le fonctionnement en architecture distribuée : quand on crée un nouveau ticket depuis la page web dans un navigateur, il est enregistré sur le serveur Flask et apparaît immédiatement dans l'application Tkinter lorsqu'on clique sur "Actualiser".

---

## Section II — Leçons apprises de ce laboratoire

Durant la réalisation de ce laboratoire 4, on a rencontré plusieurs difficultés et appris plusieurs notions importantes en architecture logicielle :

 **Le passage d'une application locale à une architecture distribuée** :  
   Au début, le problème était qu'on avait l'habitude d'appeler directement des méthodes Python et de passer des références d'objets en mémoire. En passant à une API REST, on a compris qu'on ne peut plus faire ça : il faut absolument découper les échanges en requêtes HTTP indépendantes (stateless) et sérialiser les données en JSON. On a aussi appris l'importance d'utiliser les bons codes de statut HTTP (`200 OK` pour une lecture réussie, `201 Created` après la création d'un ticket, `400 Bad Request` si un champ obligatoire manque, et `404 Not Found` si l'id du ticket n'existe pas).

 **L'efficacité du patron MVC pour la réutilisation du code** :  
   Dans les laboratoires 2 et 3, on se demandait parfois pourquoi il fallait autant séparer les responsabilités dans différentes classes. Dans ce laboratoire, on a vraiment compris l'avantage de cette séparation. Grâce au modèle MVC, nous avons pu réutiliser presque tout notre code métier existant (`Ticket`, `User`, `DescriptionFactory`, etc.) sans devoir le réécrire. De plus, quand on a ajouté l'interface web pour le bonus, on a simplement créé une nouvelle Vue en HTML/JavaScript qui communique avec l'API, sans avoir à modifier une seule ligne de notre logique métier.

 **La gestion des fichiers et des images avec une API REST** :  
   Un autre problème qu'on a rencontré concernait la description sous forme d'image. Au Lab 3, on enregistrait simplement le chemin d'accès absolu sur le disque local de notre machine. Dans une vraie architecture distribuée où le client et le serveur peuvent être sur deux machines différentes, envoyer un chemin local ne fonctionne pas car le serveur n'a pas accès au disque dur du client. Pour résoudre ce problème, on a utilisé le format `multipart/form-data` côté client et `request.files['image']` côté Flask. Cela permet de téléverser le vrai fichier binaire sur le serveur, qui le sauvegarde dans son dossier `images/` et lui attribue une URL accessible via `/api/images/<nom>`.

 **L'utilité des tests automatisés pour l'API** :  
   Enfin, on a appris qu'il est beaucoup plus rapide et efficace de valider les routes d'une API avec des tests automatisés avant de commencer à les connecter sur l'interface graphique. Nous avons écrit un fichier `test_api.py` qui teste automatiquement chaque endpoint (création de tickets, assignation, changement de statut, filtrage, gestion des utilisateurs). Grâce à ces tests, quand on a branché l'interface Tkinter et la page web sur l'API, on savait déjà que le backend fonctionnait correctement, ce qui nous a évité de perdre du temps à chercher d'où venaient les erreurs.
