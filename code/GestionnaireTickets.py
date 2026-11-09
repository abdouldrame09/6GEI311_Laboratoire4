#Classe pour gerer tout les tickets
class GestionnaireTickets:
    def __init__(self):
        self.tickets=[]

#Fonction pour ajouter un ticket
    def ajouter(self,ticket)->None:
        self.tickets.append(ticket)

#Fonction pour trouver un ticket par son id
    def trouverParId(self,id:int):
        for ticket in self.tickets:
            if ticket.ticketId == id:
                return ticket
        return None

#Fonction pour retourner tout les tickets
    def tous(self)->list:
        return self.tickets