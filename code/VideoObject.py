from DescriptionTicket import DescriptionTicket


#Classe pour une description de type video
class VideoObject(DescriptionTicket):
#Fonction pour charger la video
    def load(self)->str:
        return f"Chargement de la video : {self.chemin}"