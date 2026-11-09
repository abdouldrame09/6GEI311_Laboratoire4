from datetime import date

#liste globale de tout les utilisateurs (externe aux classes)
tousLesUtilisateurs = []

#Classe utilisteur
class User():
#Compteur statique pour generer les identifiants
    prochainId = 1

    def __init__(self,name:str,email:str):
        self.userId = User.prochainId
        User.prochainId += 1
        self.name = name
        self.email = email
        self.tickets = []
        #ajout de l'utilisateur dans la liste globale
        tousLesUtilisateurs.append(self)

#Fonction pour cree un tiket
    def createTicket(self,ticket)->None:
        ticket.createdBy = self   #le ticket connait son createur
        if ticket not in self.tickets:
            self.tickets.append(ticket)   #ajout du ticket dans la liste
        print(f"L'utilisateur {self.name} a créé le ticket #{ticket.ticketId} : '{ticket.title}'.")

#Fonction pour voir tout les tickets
    def viewTicket(self,ticket)->None:
         print(f" Ticket #{ticket.ticketId} : '{ticket.title}'  {ticket.status.value}  {ticket.priority.value} {ticket.updateDate}")
         if ticket.descriptions:
             print(" Descriptions :")
             for description in ticket.descriptions:
                 print(f"   - {description}")
             print(" Chargement des descriptions :")
             ticket.loadDescriptions()
         else:
             print(" Aucune description.")

#Fonction pour mettre a jour un ticket
    def updateTicket(self,ticket)->None:
        ticket.updateDate = date.today()  #mise a jour de la date
        print(f"L'utilisateur {self.name} a mis à jour le ticket #{ticket.ticketId}.")

#Fonction pour serialiser l'utilisateur en dictionnaire pour l'API REST
    def to_dict(self)->dict:
        return {
            "userId": self.userId,
            "name": self.name,
            "email": self.email,
            "role": "Utilisateur",
            "ticketsCount": len(self.tickets)
        }
