# -*- coding: utf-8 -*-

from configuration import *
from gurobipy import *


class LPSolver :
    """ 
        va définir les variables de contrainte nécessaires pour la résolution par PL. 
        Positions2Points : p[j][l] : ensemble des positions comprises entre j et l. -> TODO
        
    """

    def __init__(self, config):
        self.config = config
        self.nbMove = config.getNbCoupMax() # nombre de mouvements max autorisés
        self.model = Model()
        self.marqueurs = range(36)
        self.moves = range(self.nbMove+1)

        self.initArrays()
        self.createDecisionsVariables()
        self.createObjective()
        self.createConstraints()

        print(len(self.model.getConstrs()), len(self.model.getVars()))
        self.model.optimize()
        #self.model.optimize()


    def solve(self, path):
        """ Demande la résolution du modèle et écrit l'ensemble des variables valeurs de y[i][j][k][l] dans le fichier de chemin path """
        self.model.optimize()

        content = ""
        for idVehicule in self.y.keys():
                for j in self.possiblesMarqueurs[idVehicule]:
                    for l in self.possiblesMarqueurs[idVehicule]:
                        if j != l:
                            for k in self.moves():
                                if y[i][j][k][l].X == 1:
                                    content += "%s,%d,%d,%d\n".format(idVehicule, i, j, k)

        with open(path, "w") as file:
            file.write(content)



####################################### Méthodes d'initialisations ####################################### 


    def initArrays(self):
        """ Initialise l'ensembles des tableaux et matrices nécessaires à l'établissement des variables, contraintes et de la fonction objectif """
        self.initLongueurs() # correspond à v
        self.initPositions2Points() # correspond à p
        self.initPositionsVehicules() # correspond à m   
        self.initPossiblesPositions() # créé x, y, z et les initialise selon la configuration passée en param


    def createDecisionsVariables(self):
        """ Créé l'ensemble des variables de décisions nécessaires à la résolution du problème. """
        self.x, self.y, self.z = {}, {}, {}

        for vehicule in self.config.getVehicules():
            # Création de toutes les variables de décision associé au véhicule 
            idVehicule = vehicule.getIdVehicule()
            self.x[idVehicule] = {j:[self.model.addVar(0, 1, vtype=GRB.BINARY) for k in self.moves] for j in self.possiblesMarqueurs[idVehicule]}
            self.z[idVehicule] = {j:[self.model.addVar(0, 1, vtype=GRB.BINARY) for k in self.moves] for j in self.possiblesPositions[idVehicule]}
            self.y[idVehicule] = {j:{l:[self.model.addVar(0, 1, vtype=GRB.BINARY) for k in self.moves] for l in self.possiblesMarqueurs[idVehicule] if l != j} for j in self.possiblesMarqueurs[idVehicule]}
        
        self.model.update()

    def createObjective(self, objectiveType="RHM"):
        """ Défini l'objectif du modèle en fonction du type d'objectif passé en paramètre.
            L'objectif est soit de type "RHM", minimisant le nombre de mouvement, soit de type "RHC", minimisant le nombre de case parcourue.
        """
        objective = LinExpr()
        # A OPTIMISER, Développer rapidement parceque flemme et envie de jouer (présaison open omg too op ggwp rito)
        for vehiculeList in self.y.values():
            for j,marqueurList in vehiculeList.items():
                for l,deplList in marqueurList.items():
                    for movementVariable in deplList:
                        coeff = 1 if objectiveType == "RHM" else len(self.positionEntre2Points(j,l))
                        objective.addTerms(coeff, movementVariable)

        self.model.setObjective(objective, GRB.MINIMIZE)
        self.model.update()


    def createConstraints(self):
        """ Créé l'ensemble des contraintes nécéssaire à la résolution de la configuration RushHour """
        self.addPositionConstraints() # contraintes de type 1, 2 et 3
        self.addMovementConstraints() # contraintes de type 4, 5, 6, 7
        self.addInitialisationConstraints() # contraintes d'initialisations
        self.model.update()




#######################################   Définition des tableaux d'attributs ####################################### 

    def initPossiblesPositions(self):
        """ Créé une liste des positions possibles que peut prendre chaque véhicule """
        self.possiblesPositions = {}
        self.possiblesMarqueurs = {}

        for vehicule in self.config.getVehicules():

            idVehicule = vehicule.getIdVehicule()
            orientation = vehicule.getOrientation()
            typeVehicule = vehicule.getTypeVehicule()

            start = vehicule.getMarqueur()%6 if orientation == Orientation.BAS else vehicule.getMarqueur()//6 * Orientation.BAS

            self.possiblesPositions[idVehicule] = list(range(start, start + 5*orientation + 1, orientation))
            self.possiblesMarqueurs[idVehicule] = list(range(start, start + (5 - (typeVehicule - 1))*orientation + 1, orientation))

    def initLongueurs(self):
        """ Défini la longueur de tous les véhicules de config

            Paramètres : 
                - une configuration des voitures
        """
        self.longueurs = {}
        for vehicule in self.config.getVehicules():
            self.longueurs[vehicule.getIdVehicule()] = vehicule.getTypeVehicule()

    def getLongueurs(self):
        """ Renvoie la longueur de tous les véhicules de config"""
        return self.longueurs


    def initPositionsVehicules(self):
        """ Pour chaque véhicule et pour chaque case, défini toutes les cases occupées

            Paramètres : 
                    - une configuration des voitures
        """
        self.positionsVehicules = {}
        for vehicle in self.config.getVehicules():
            currentList = []
            # pour chaque positions de la grille
            for j in range(36):
                positions = []
                indexMax = vehicle.getOrientation() * vehicle.getTypeVehicule()
                # si le véhicule ne sort pas de la grille
                if (j + indexMax <36):
                    positions = self.positions2Points[j][j + indexMax]
                currentList.append(positions)

            self.positionsVehicules[vehicle.getIdVehicule()] = currentList

    def getPositionsVehicules(self):
        """ Renvoie la liste de toutes les cases occupées pour un véhicule et une case donnée """
        return self.positionsVehicules

    def initPositions2Points(self):
        """ Défini la matrice p[][] qui contient pour tout i,j l'ensemble des positions entre ces deux marqueurs.
            Si les cases ne sont pas alignées verticalement ou horizontalement, le tableau renverra une liste vide pour la case correspondante
        """
        self.positions2Points = []
        for i in range(36):
            currentList = []
            for j in range(36):
                positions = []
                step = 0
                # si les 2 points sont alignés horizontalement
                if(i//6 == j//6):
                    step = 1

                # si les deux points sont alignés verticalement
                elif(i%6 == j%6):
                    step = 6

                # pour parcourir dans l'autre sens si j est avant i
                coef = 1 if i<=j else -1

                # si les deux points sont alignés verticalement ou horizontalement
                if(step !=0):
                    for k in range(i, j + (1 * coef), step * coef):
                        positions.append(k) # on ajoute chaque point compris entre i et j

                currentList.append(positions)
            self.positions2Points.append(currentList)


    def getPositions2Points(self):
        """ retourne un tableau [pour toutes les cases j][pour toutes les cases l] qui est l'ensemble des positions comprises entre j et l."""
        return self.positions2Points




#######################################   Définition des contraintes ####################################### 


    def addPositionConstraints(self):
        """ Trois types de contraintes sont ajoutées dans cette méthode
                Un seul véhicule dans chaque case a chaque tour. # 2
                Seule vi cases sont occupées par le véhicule i dans sa rangée. #3
                zi,m,k = 1 pour toutes m cases occupées par un véhicule i.

        """
        for k in self.moves:
            for idVehicule in self.z.keys():
                # pour chaque tour et chaque véhicule, la somme de ces variables z a 1 est égal a la longueur du véhicule.
                self.model.addConstr(quicksum((self.z[idVehicule][j][k] for j in self.possiblesPositions[idVehicule])), GRB.EQUAL, self.longueurs[idVehicule]) #3

                for j in self.possiblesMarqueurs[idVehicule]:
                    # pour vehicule, tour et positions du vehicule possible, les z correspondant aux positions du véhicule sont a 1
                    self.model.addConstr(self.longueurs[idVehicule]*self.x[idVehicule][j][k] - quicksum(self.z[idVehicule][l][k] for l in self.positionsVehicules[idVehicule][j]), GRB.LESS_EQUAL, 0)

            for j in self.marqueurs:
                # pour chaque tour et chaque marqueur, il y a au plus un seul véhicule dans la case
                self.model.addConstr(quicksum((self.z[idVehicule][j][k] for idVehicule in self.z.keys() if j in self.possiblesPositions[idVehicule])), GRB.LESS_EQUAL, 1)

    def addMovementConstraints(self):
        """ Quatre types de contraintes sont ajoutées dans cette méthode:
                un véhicule ne peut se déplacer que si l'espace entre les deux cases est vide (4)
                au plus un véhicule est déplacé par tour (5)
                le dernier mouvement est celui ou le véhicule "g" est au marqueur 16 (6)
                lors d'un mouvement, le marqueur du véhicule est bien mis à jour (7)
        """
        for k in self.moves:
            # le nombre de véhicule déplacé au tour k
            nbVehiculeMoved = LinExpr()

            for idVehicule in self.y.keys():
                for j in self.possiblesMarqueurs[idVehicule]:
                    for l in self.possiblesMarqueurs[idVehicule]:
                        if j != l:

                            # ajoute la variable mouvement du vehicule i de j à l au tour k
                            nbVehiculeMoved.addTerms(1, self.y[idVehicule][j][l][k])

                            # Dans tous les tours suivant le premier, le marqueur du vehicule est mis à jour en cas de mouvement
                            if k!=0:
                                self.model.addConstr(self.y[idVehicule][j][l][k-1] - self.x[idVehicule][l][k], GRB.LESS_EQUAL, 0) # (7)

                            # idVehicule peut se déplacer de j à l uniquement si cet espace est vide.
                            for p in self.positions2Points[j][l]:
                                nbVehiculeBetween = LinExpr()
                                for otherVehicule in self.y.keys():
                                    if otherVehicule != idVehicule and p in self.possiblesPositions[otherVehicule]:
                                        nbVehiculeBetween.addTerms(1, self.z[otherVehicule][p][k])
                                # quicksum([self.z[otherVehicule][p][k-1] for otherVehicule in self.y.keys() if otherVehicule != idVehicule and p in self.possiblesPositions[otherVehicule]])
                                self.model.addConstr(self.y[idVehicule][j][l][k] - (1-nbVehiculeBetween), GRB.LESS_EQUAL, 0) # (4)
            

            # Le dernier mouvement est celui ou g est en 16. Avant cela il y a nécessairement un mouvement chaque tour
            self.model.addConstr(nbVehiculeMoved - (1-self.x["g"][16][k]), GRB.EQUAL, 0) #(6)
            # A chaque tour au plus un véhicule est bougé, utile dans notre conception ?
            self.model.addConstr(nbVehiculeMoved, GRB.LESS_EQUAL, 1) #(5)

    def addInitialisationConstraints(self):
        """ Ajoute les contraintes d'initialisation représentant la configuration courante """
        for vehicule in self.config.getVehicules():
            idVehicule = vehicule.getIdVehicule()
            self.model.addConstr(self.x[idVehicule][vehicule.getMarqueur()][0], GRB.EQUAL, 1)
            print(idVehicule, vehicule.getMarqueur())
            # for pos in self.positionsVehicules[idVehicule][vehicule.getMarqueur()]: Une contrainte les met à 1 automatiquement, pas nécessaire.
            #     self.model.addConstr(self.z[idVehicule][pos][0], GRB.EQUAL, 1)
                            
def main(): 
# if __name__ == "__main__":
    conf = Configuration.readFile("../puzzles/avancé/jam30.txt")
    conf.setNbCoupMax(50)
    lp = LPSolver(conf)

    # [print(pl.getMatricePresence()[i]) for i in range(len(pl.getMatricePresence()))]
    # [print(pl.getMatriceOccupe()[i]) for i in range(len(pl.getMatriceOccupe()))]
    # print(pl.getPositions2Points())
    # [print(pl.getPositionsVehicules()[i]) for i in range(len(pl.getPositionsVehicules()))]

main()