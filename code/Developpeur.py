from User import User
from Statut import Statut

#liste globale de tout les developpeurs (externe aux classes)
tousLesDeveloppeurs = []

#Classe Developpeur (herite de User)
class Developpeur(User):
    def __init__(self,name:str,email:str):
        super().__init__(name=name,email=email)
        #ajout du developpeur dans la liste globale
        tousLesDeveloppeurs.append(self)

#Fonction pour assigner un ticket a un developpeur
    def assignTicket(self,ticket,dev)->None:
        ticket.assignTo(dev)   #assignation du ticket au developpeur

#Fonction pour valider un ticket
    def validateTicket(self,ticket)->None:
        ticket.updateStatus(Statut.VALIDATION)

#Fonction pour fermé un ticket
    def closeTicket(self,ticket)->None:
        ticket.updateStatus(Statut.TERMINE)

#Fonction pour voir tout les tickets
    def viewAllTickets(self,gestionnaire)->list:
        if not gestionnaire.tous():
            print("Aucun ticket disponible.")
            return []
        for ticket in gestionnaire.tous():
            print(f" Ticket #{ticket.ticketId} : '{ticket.title}'  [{ticket.status.value}]  {ticket.priority.value} {ticket.updateDate}")
        return gestionnaire.tous()

#Fonction pour serialiser le developpeur en dictionnaire pour l'API REST
    def to_dict(self)->dict:
        return {
            "userId": self.userId,
            "name": self.name,
            "email": self.email,
            "role": "Developpeur",
            "ticketsCount": len(self.tickets)
        }
