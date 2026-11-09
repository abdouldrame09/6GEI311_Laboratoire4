import os
from DescriptionTicket import DescriptionTicket

#Classe pour une description de type image
class ImageObject(DescriptionTicket):
#Fonction pour charger l'image
    def load(self)->str:
        return f"Chargement de l'image : {self.chemin}"

#Fonction pour serialiser en dictionnaire pour l'API REST
    def to_dict(self)->dict:
        return {
            "type": "IMAGE",
            "chemin": self.chemin,
            "nom_fichier": os.path.basename(self.chemin)
        }
