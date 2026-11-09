from enum import Enum

#Enumeration pour le statut du ticket
class Statut(Enum):
    OUVERT="OUVERT"
    ASSIGNE="ASSIGNÉ"
    VALIDATION="VALIDATION"
    TERMINE="TERMINÉ"