from DescriptionTicket import DescriptionTicket

#Classe pour une description de type texte
class TextObject(DescriptionTicket):
#Fonction pour charger le texte
    def load(self)->str:
        return f"Chargement du texte : {self.chemin}"

#Fonction pour serialiser en dictionnaire pour l'API REST
    def to_dict(self)->dict:
        return {
            "type": "TEXTE",
            "chemin": self.chemin,
            "contenu": self.chemin
        }
