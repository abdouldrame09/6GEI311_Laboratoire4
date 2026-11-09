from TextObject import TextObject
from ImageObject import ImageObject
from VideoObject import VideoObject
from TypeDescription import TypeDescription

#Classe pour creer les descriptions
class DescriptionFactory:
#Fonction pour creer une description selon son type
    @staticmethod
    def createDescription(typeDescription:TypeDescription,chemin:str):
        if typeDescription == TypeDescription.TEXTE:
            return TextObject(chemin)
        elif typeDescription == TypeDescription.IMAGE:
            return ImageObject(chemin)
        elif typeDescription == TypeDescription.VIDEO:
            return VideoObject(chemin)
        else:
            print("Type de description invalide.")
            return None