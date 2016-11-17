# -*- coding: utf-8 -*-

from configuration import *

class LPSolver :
    """ 
        va définir les variables de contrainte nécessaires pour la résolution par PL. 
        Positions2Points : p[j][l] : ensemble des positions comprises entre j et l. -> TODO
        
    """

    def __init__(self, config):

        self.nbMove = config.getNbCoupMax() # nombre de mouvements max autorisés

        
        self.initLongueurs(config)
        self.initPosition2Points()
        self.initPositionsVehicules(config)

        self.matricePresence = LPSolver.initTab3D(len(config.getVehicules()), 36, self.nbMove + 1)
        self.setMatricePresence(config, 0)

        self.matriceOccupe = LPSolver.initTab3D(len(config.getVehicules()), 36, self.nbMove + 1)
        self.setMatriceOccupe(config, 0)

        self.matriceMouvement = []
        [self.matriceMouvement.append(PL.initTab3D(36, 36, self.nbMove)) for i in range(len(config.getVehicules()))]
        

    def setMatricePresence(self, config, step):
        """ 
            Modifie une matrice de la forme : [pour chaque voiture "i" ][pour chaque case "j" ][pour chaque étape "step"]
            Si une voiture i a son marqueur sur une case j à une étape donnée "step", la case de la matrice correspondante indiquera 1, 0 sinon

            Paramètres : 
                - une configuration des voitures
                - une étape "step"

        """

        for i in range(0, len(config.getVehicules())):
            self.matricePresence[i][ config.getVehicules()[i].getMarqueur() ][step] = 1

    def getMatricePresence(self):
        """ 
            Renvoie une matrice de la forme : [pour chaque voiture "i" ][pour chaque case "j" ][pour chaque étape "step"]
            Si une voiture i a son marqueur sur une case j à une étape donnée "step", la case de la matrice correspondante indiquera 1, 0 sinon
        """
        return self.matricePresence


    def setMatriceOccupe(self, config, step):
        """
            Modifie une matrice de la forme : [pour chaque voiture "i" ][pour chaque case "j" ][pour chaque étape "step"]
            Si une voiture i occupe une case j à une étape donnée "step", la case de la matrice correspondante indiquera 1, 0 sinon

            Paramètres : 
                - une configuration des voitures
                - une étape "step"
        """

        for i in range(0, len(config.getVehicules())):
            vehicle = config.getVehicules()[i]
            for positions in self.positionsVehicules[i][vehicle.getMarqueur()]:
                self.matricePresence[i][ positions ][step] = 1

    def getMatriceOccupe(self):
        """ 
            Renvoie une matrice de la forme : [pour chaque voiture "i" ][pour chaque case "j" ][pour chaque étape "step"]
            Si une voiture i occupe une case j à une étape donnée "step", la case de la matrice correspondante indiquera 1, 0 sinon
        """
        return self.matriceOccupe

    def setMatriceMouvement(self, config, step):
        """ 
            modifie une matrice de la forme [Pour chaque voiture i][pour chaque case j][Pour chaque case l][pour chaque étape]
            Va modifier si il y a eu un mouvement de k vers l entre l'étape k-1 et l'étape k
            S'il y a eu un mouvement, indique 1, sinon 0

            Paramètres : 
                - une configuration des voitures
                - une étape "step"
        """

        if step>0:
            for i in range(0, len(config.getVehicules())):
                previousPointer = -1
                currentPointer = -1

                # ne sont modifiés que s'il y a eu un changement de la position du pointeur au cours du k-eme mouvement
                for j in range(36):
                    
                    # ne sera vérifié que si on avait un marqueur à une étape en j qui n'y est plus
                    if(self.matricePresence[i][j][step - 1] < self.matricePresence[i][j][step]):
                        previousPointer = j

                    # ne sera vérifié que si on a un pointeur qui n'était pas présent à une étape en j et qui y est maintenant
                    elif(self.matricePresence[i][j][step - 1] > self.matricePresence[i][j][step]):
                        currentPointer = j

                if( previousPointer != -1 and currentPointer != -1):
                    self.matriceMouvement[i][previousPointer][currentPointer][step] = 1


    def getMatriceMouvement(self):
        """ 
            renvoie une matrice de la forme [Pour chaque voiture i][pour chaque case j][Pour chaque case l][pour chaque étape]
            Va modifier si il y a eu un mouvement de k vers l entre l'étape k-1 et l'étape k
            S'il y a eu un mouvement, indique 1, sinon 0
        """
        return self.matriceMouvement

    def initLongueurs(self, config):
        """ Défini la longueur de tous les véhicules de config

        Paramètres : 
                - une configuration des voitures
        """
        self.longueurs = [0]*len(config.getVehicules())
        for i in range(0, len(config.getVehicules())):
            self.longueurs[i] = config.getVehicules()[i].getTypeVehicule()

    def getLongueurs(self, config):
        """ Renvoie la longueur de tous les véhicules de config"""

        return self.longueurs

    def initPositionsVehicules(self, config):
        """ Pour chaque véhicule et pour chaque case, défini toutes les cases occupées

            Paramètres : 
                    - une configuration des voitures
        """

        self.positionsVehicules = []
        for i in range(0, len(config.getVehicules())):

            vehicle = config.getVehicules()[i] 
            self.positionsVehicules.append([])

            # pour chaque positions de la grille
            for j in range(36):

                listToAdd = []

                # si le véhicule est tourné vers la droite
                index = vehicle.getTypeVehicule() -1

                # si le véhicule est tourné vers le bas
                if(vehicle.getOrientation() != 1):
                    index = 6 * (vehicle.getTypeVehicule() -1)
                    
                # si le véhicule ne sort pas de la grille
                if (j + index <36):
                    listToAdd = self.positions2Points[j][j + index]

                self.positionsVehicules[i].append(listToAdd)

    def getPositionsVehicules(self):
        """ Renvoie la liste de toutes les cases occupées pour un véhicule et une case donnée """

        return self.positionsVehicules

    def initPosition2Points(self):
        """ 
            défini un tableau [pour toutes les cases i][pour toutes les cases j] qui est l'ensemble des positions comprises entre i et j.
            Si les cases ne sont pas alignées verticalement ou horizontalement, le tableau renverra une liste vide pour la case correspondante
        """

        self.positions2Points = []
        for i in range(36):
            self.positions2Points.append([])

            for j in range(36):
                listToAdd = []
                step = 0

                # si les 2 points sont alignés horizontalement
                if(i//6 == j//6):
                    step = 1

                # si les deux points sont alignés verticalement
                elif(i%6 == j%6):
                    step = 6

                # pour parcourir dans l'autre sens si j est avant i
                coef = 1
                if(i>j):
                    coef = -1

                # si les deux points sont alignés verticalement ou horizontalement
                if(step !=0):
                    for k in range(i, j + (1 * coef), step * coef):
                        listToAdd.append(k) # on ajoute chaque point compris entre i et j

                self.positions2Points[i].append(listToAdd)


    def getPositions2Points(self):
        """ retourne un tableau [pour toutes les cases j][pour toutes les cases l] qui est l'ensemble des positions comprises entre j et l."""

        return self.positions2Points


    @staticmethod
    def initTab3D(x, y, z):
        """ créé et initialise un tableau à 3 dimensions aux tailles données en paramètre """

        tab = []
        for i in range(x):
            tab.append([])
            for j in range(y):
                tab[i].append([0] * z)
        return tab

def main():
# if __name__ == "__main__":
    conf = Configuration.readFile("../puzzles/avancé/jam30.txt")
    pl = PLSolver(conf)
    # [print(pl.getMatricePresence()[i]) for i in range(len(pl.getMatricePresence()))]
    # [print(pl.getMatriceOccupe()[i]) for i in range(len(pl.getMatriceOccupe()))]
    # print(pl.getPositions2Points())
    # [print(pl.getPositionsVehicules()[i]) for i in range(len(pl.getPositionsVehicules()))]

main()