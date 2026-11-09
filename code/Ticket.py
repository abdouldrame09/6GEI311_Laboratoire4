from datetime import date
from Statut import Statut
from Priorite import Priorite

#Classe Ticket
class Ticket():
#Compteur statique pour generer les identifiants
    prochainId = 1

    def __init__(self,title:str,status:Statut=Statut.OUVERT,priority:Priorite=Priorite.NORMALE):
        self.ticketId=Ticket.prochainId
        Ticket.prochainId+=1
        self.title=title
        self.status=status
        self.priority=priority
        self.creationDate=date.today()
        self.updateDate=date.today()
        self.descriptions=[]
        self.createdBy=None
        self.assignedTo=None

#Fonction pour assigner un ticket a un utilisateur
    def assignTo(self,user)->None:
        self.assignedTo=user    #assignation du ticket a l'utilisateur
        self.status=Statut.ASSIGNE   #mise a jour du statut
        self.updateDate=date.today()  #mise a jour de la date
        if hasattr(user, 'tickets') and self not in user.tickets:
            user.tickets.append(self)  #ajout du ticket a l'utilisateur
        print(f"Le ticket #{self.ticketId} a été assigné à {user.name}.")

#Fonction pour mettre a jour le status d'un ticket
    def updateStatus(self,status:Statut)->None:
        self.status=status   #mise a jour du statut
        self.updateDate=date.today()  #mise a jour de la date
        print(f"Le statut du ticket #{self.ticketId} à été mise à jour au statut {self.status.value}")

#Fonction pour mettre a jour les informations du ticket
    def updateInfo(self,title:str=None,priority:Priorite=None)->None:
        if title is not None:
            self.title=title
        if priority is not None:
            self.priority=priority
        self.updateDate=date.today()  #mise a jour de la date

#Fonction pour ajouter une description au ticket
    def addDescription(self,description)->None:
        self.descriptions.append(description)   #ajout de la description dans la liste
        self.updateDate=date.today()  #mise a jour de la date
        print(f"Description ajoutée au ticket #{self.ticketId}.")

#Fonction pour charger toute les descriptions
    def loadDescriptions(self)->None:
        for description in self.descriptions:
            print(description.load())

#Fonction pour serialiser le ticket en dictionnaire pour l'API REST
    def to_dict(self)->dict:
        return {
            "ticketId": self.ticketId,
            "title": self.title,
            "status": self.status.value,
            "priority": self.priority.value,
            "creationDate": self.creationDate.isoformat() if hasattr(self.creationDate, 'isoformat') else str(self.creationDate),
            "updateDate": self.updateDate.isoformat() if hasattr(self.updateDate, 'isoformat') else str(self.updateDate),
            "createdBy": self.createdBy.to_dict() if self.createdBy else None,
            "assignedTo": self.assignedTo.to_dict() if self.assignedTo else None,
            "descriptions": [d.to_dict() if hasattr(d, 'to_dict') else {"type": "RAW", "chemin": str(d), "contenu": str(d)} for d in self.descriptions]
        }
