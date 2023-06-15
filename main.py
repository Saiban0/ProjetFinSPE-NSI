import pyxel

##Variables globales
max_x,max_y=224,120
min_x,min_y=32,24
type_entites=(0,1,2,3,4,5,6)
def creation_entite():
    """
    Fonction permettant de générer une entitée aléatoire
    """
    rand_type = pyxel.rndi(0,len(type_entites)-1)
    if rand_type == 0:
        rand_y = pyxel.rndi(min_y, max_y - 14)
        return Rayon(min_x, rand_y, rand_type)
    elif rand_type==1:
        rand_x = pyxel.rndi(min_x, max_x - 14)
        return Rayon(rand_x, min_y, rand_type)
    elif rand_type==2:
        rand_y = pyxel.rndi(min_y, max_y - 14)
        return Collectible(max_x-14,rand_y,rand_type)
    elif rand_type==3:
        rand_y = pyxel.rndi(min_y, max_y - 14)
        return Collectible(max_x - 14, rand_y, rand_type)
    elif rand_type==4:
        rand_y = pyxel.rndi(min_y, max_y - 14)
        return Rayon(min_x, rand_y, rand_type)
    elif rand_type==5:
        rand_x = pyxel.rndi(min_x, max_x - 14)
        return Rayon(rand_x, min_y, rand_type)
    elif rand_type==6:
        rand_y=pyxel.rndi(min_y,max_y-14)
        return Collectible(max_x-14,rand_y,rand_type)



class App:
    def __init__(self):
        pyxel.init(256, 128, fps=60,title="Sivouplé j'ai faim") ##Définition de la fenêtre
        pyxel.load("assets.pyxres") ##Chargement des assets
        self.nouvelle_partie()
        pyxel.run(self.update, self.draw) ##Lancement du jeu

    def nouvelle_partie(self):
        """lance une nouvelle partie en initialisant tout"""
        self.player = Player(128, 88)  # Initialisation du joueur au milieu de la zone de jeu
        self.rayons = []  ##Liste des rayons actifs
        self.timer = 0  ##Timer de la partie
        ##Liste des coeurs à afficher
        self.coeurs = [Coeur(4, 16, True), Coeur(12, 16, True), Coeur(20, 16, True), Coeur(4, 24, True),Coeur(12, 24, True),
                       Coeur(20, 24, True), Coeur(4, 32, True), Coeur(12, 32, True),Coeur(20, 32, True), Coeur(12, 40, True),
                       Coeur(224 + 4, 16, False, bonus=True), Coeur(224 + 12, 16, False, bonus=True),Coeur(224 + 20, 16, False, bonus=True),
                       Coeur(224 + 4, 24, False, bonus=True), Coeur(224 + 12, 24, False, bonus=True),Coeur(224 + 20, 24, False, bonus=True),
                       Coeur(224 + 4, 32, False, bonus=True), Coeur(224 + 12, 32, False, bonus=True),Coeur(224 + 20, 32, False, bonus=True),
                       Coeur(224 + 12, 40, False, bonus=True)]

        self.collectibles = []  ##Liste des collectibles actifs
        self.tirs = []  ##Liste des tirs actifs
        self.explosions_liste = []  # Liste des animations d'explosions actives
        self.score = 0  ##Score du joueur
        pyxel.mouse(False)

#######################################################################################################################
    #UPDATE
#######################################################################################################################

    def update(self):
        """
        Mise à jour des positions et des états.
        """
        if not self.verif_game_over(): ##Vérification du game over
            ##Inputs joueur
            if pyxel.btn(pyxel.KEY_UP) or pyxel.btn(pyxel.KEY_Z):##Déplacements en haut
                self.player.move(0,-1.5)
                self.player.direction="Haut"
            if pyxel.btn(pyxel.KEY_DOWN) or pyxel.btn(pyxel.KEY_S): ##Déplacements en bas
                self.player.move(0,1.5)
                self.player.direction="Bas"
            if pyxel.btn(pyxel.KEY_LEFT) or pyxel.btn(pyxel.KEY_Q):##Déplacements à gauche
                self.player.move(-1.5,0)
                self.player.direction="Gauche"
            if pyxel.btn(pyxel.KEY_RIGHT) or pyxel.btn(pyxel.KEY_D):##Déplacements à droite
                self.player.move(1.5,0)
                self.player.direction="Droite"
            if pyxel.btnr(pyxel.KEY_SPACE) or pyxel.btnr(pyxel.MOUSE_BUTTON_LEFT): ##Tirs du joueur
                if not self.player.touche:
                    self.tirs.append(self.player.tir())
            if pyxel.btnr(pyxel.KEY_X) or pyxel.btnr(pyxel.MOUSE_BUTTON_RIGHT): ## Utilisation d'une bouteille
                self.player.bouteille()

            if not self.verif_victoire(): ##Vérification de la victoire du joueur
                self.timer += 1  ##augmentation du timer de la partie à chaque exécution de le fonction

                ##Augmentation du timer  des rayons
                for rayon in self.rayons:
                    rayon.timer+=1
                    if rayon.timer>=60: #Si le rayon a une seconde, il s'active
                        rayon.etat=True
                    if rayon.timer>=3*60: #Si le rayon a trois secondes, il disparait
                        self.rayons.remove(rayon)


                ##Ajout d'une entité toutes les secondes
                if self.timer%60==1:
                    nouv=creation_entite()
                    if type(nouv)==Rayon:
                        self.rayons.append(nouv)
                    else:
                        self.collectibles.append(nouv)
                    if self.player.touche:  ##Réinitialisation de l'état du joueur
                        self.player.touche = False

                ##Collisions avec les rayons
                for rayon in self.rayons:
                    if (rayon.type==0 or rayon.type==4) and rayon.etat:
                        if rayon.y<self.player.y<rayon.y+8 or rayon.y<self.player.y+12<rayon.y+8:
                            if self.player.touche==False:
                                self.degats()
                                self.score-=15
                    if (rayon.type == 1 or rayon.type==5) and rayon.etat:
                        if rayon.x < self.player.x < rayon.x + 8 or rayon.x < self.player.x+14 < rayon.x + 8:
                            if self.player.touche==False:
                                self.degats()
                                self.score-=15


                ##Déplacements des entitées
                for coll in self.collectibles:
                    if min_x<=coll.x<=max_x:
                        coll.move()
                    elif coll in self.collectibles:
                        self.collectibles.remove(coll)
                for rayon in self.rayons:
                    if rayon.type==4:
                        if min_y<=rayon.y<=max_y:
                            rayon.move()
                            pyxel.play(1, 2)
                    elif rayon.type==5:
                        if min_x<=rayon.x<=max_x:
                            rayon.move()
                            pyxel.play(1, 2)
                for tir in self.tirs:
                    if min_x<=tir.x<=max_x-8 and min_y<=tir.y<=max_y:
                        tir.move()
                    else:
                        self.tirs.remove(tir)

                ##Collisions avec les collectibles
                for coll in self.collectibles:
                    if coll.x<=self.player.x<=coll.x+12 and coll.y<=self.player.y<=coll.y+14:
                        if coll.type==2:
                            if self.player.touche==False:
                                self.degats()
                                pyxel.sound(0)
                                self.score-=10
                        elif coll.type==3:
                            self.soin()
                        elif coll.type==6:
                            self.player.bouteilles+=1
                            pyxel.play(0,3)
                        self.collectibles.remove(coll)
                    if coll.x<=self.player.x+12<=coll.x+12 and coll.y<=self.player.y<=coll.y+14:
                        if coll.type == 2:
                            if self.player.touche == False:
                                self.degats()
                                self.score-=10
                        elif coll.type==3:
                            self.soin()
                        elif coll.type==6:
                            self.player.bouteilles+=1
                            pyxel.play(0,3)
                        self.collectibles.remove(coll)
                    if coll.x<=self.player.x<=coll.x+12 and coll.y<=self.player.y+14<=coll.y+14:
                        if coll.type == 2:
                            if self.player.touche == False:
                                self.degats()
                                self.score-=10
                        elif coll.type==3:
                            self.soin()
                        elif coll.type==6:
                            self.player.bouteilles+=1
                            pyxel.play(0,3)
                        self.collectibles.remove(coll)
                    if coll.x<=self.player.x+12<=coll.x+12 and coll.y<=self.player.y+14<=coll.y+14:
                        if coll.type == 2:
                            if self.player.touche == False:
                                self.degats()
                                self.score-=10
                        elif coll.type==3:
                            self.soin()
                        elif coll.type==6:
                            self.player.bouteilles+=1
                            pyxel.play(0,3)
                        self.collectibles.remove(coll)


                ##Collisions missiles collectibles
                for coll in self.collectibles:
                    for tir in self.tirs:
                        if (coll.x<=tir.x<=coll.x+14 or coll.x<=tir.x+8<=coll.x+14) and coll.y<=tir.y+1<=coll.y+14:
                            self.explosions_creation(coll.x, coll.y)
                            self.collectibles.remove(coll)
                            self.tirs.remove(tir)
                            self.score += 10

                # Evolution de l'animation des explosions
                self.explosions_animation()
            else: ##Ecran de victoire
                self.rayons = []  ##Vide les rayons actifs
                self.collectibles = []  ##Vide les collectibles actifs
                self.tirs = []  ##Vide les tirs actifs
                self.explosions_liste = []  ## Vide les explosions actives
                self.player.victoire=True ##Afin de sortir de l'écran

                ##Continuer la partie
                if 2<=self.player.x<=42 and 72<=self.player.y<=82: ##Collisions avec le coeur de fin
                    self.timer=0
                    self.player.x,self.player.y=128, 88 ##Téléportation du joueur à la position initiale
                    self.player.victoire=False  ##Afin de re-bloquer le joueur
                    self.player.touche= False ##Réinitialise l'état du joueur

        else:
            ##Collisions bouton restart
            if pyxel.btnr(pyxel.MOUSE_BUTTON_LEFT):
                if max_x//2-8<=pyxel.mouse_x<=max_x//2+28 and max_y//2+8<=pyxel.mouse_y<=max_y//2+18:
                    self.nouvelle_partie()



#######################################################################################################################
# UPDATE FIN
#######################################################################################################################

    def explosions_creation(self, x, y):
        """explosions aux points de collision entre deux objets"""
        self.explosions_liste.append([x, y, 0])
        pyxel.play(2, 6)

    def explosions_animation(self):
        """animation des explosions"""
        for explosion in self.explosions_liste:
            explosion[2] += 1
            if explosion[2] == 24:
                self.explosions_liste.remove(explosion)

    def degats(self):
        """
        Permet de gérer les dégats encaissés par le joueur
        :return: vide car seul utilitée est de ne pas modifier toute la liste des coeurs
        """
        self.player.pv -= 1
        pyxel.play(0,0)
        self.player.touche = True
        for c in range(len(self.coeurs)-1,-1,-1):
            if self.coeurs[c].etat:
                self.coeurs[c].etat=False
                return

    def soin(self):
        """
        Permet de soigner le joueur
        :return: vide car seul utilitée est de ne pas modifier toute la liste des coeurs
        """
        pyxel.play(0, 1)
        for coeur in range(len(self.coeurs)-1,0,-1):
            if self.coeurs[coeur].etat==False:
                self.coeurs[coeur].etat=True
                self.player.pv+=1
                return

    def verif_game_over(self):
        """
        Permet de déterminer si le joueur a encore des vies
        :return: booléen déterminant si le joueur n'a plus de vie
        """
        cpt=0
        for coeur in self.coeurs:
            if coeur.etat:
                cpt+=1
        if cpt==0:
            return True
        return False

    def verif_victoire(self):
        if self.timer==60*60:
            return True



    def draw(self):
        """
        Affichage global
        """
        pyxel.cls(0)  ## réinitialisation de l'image
        ##Zone de jeu
        pyxel.rectb(min_x,min_y,192,96,7)
        pyxel.rect(min_x-2,min_y,2,96,10)
        pyxel.rect(min_x, min_y-2, 192, 2, 10)
        pyxel.rect(max_x, min_y, 2, 96, 10)
        pyxel.rect(min_x, max_y, 192, 2, 10)

        pyxel.text(max_x//2,16,str(self.timer//60)+" s",10) ##Affichage du timer
        pyxel.text((max_x//2)-8,4,"Boucliers ="+str(self.player.bouteilles),3) ##Affichage du nombre de boucliers
        pyxel.text(4,4,"Vies ="+str(self.player.pv),3) ##Affichage des vies
        pyxel.text(max_x-16,4,"Score ="+str(self.score),3) ##Affichage du score
        for c in self.coeurs:  ##Affichage des coeurs
            c.draw()

        ##Affichage des entités
        self.player.draw() #Affichage du joueur
        for rayon in self.rayons: ##Affichage des rayons
            rayon.draw()
        for coll in self.collectibles:  ##Affichage des collectibles
            coll.draw()
        for tir in self.tirs:       ##Affichage des missiles
            tir.draw()
        for explosion in self.explosions_liste:  # Affichage des explosions
            pyxel.circb(explosion[0] + 4, explosion[1] + 4, 2 * (explosion[2] // 4), 8 + explosion[2] % 3)

        if self.verif_game_over(): ##Affichage de l'écran de game over
            self.draw_game_over()
        if self.verif_victoire(): ##Affichage de la victoire
            self.draw_victoire()



    def draw_game_over(self):
        """Affichage utilisé en cas de game over"""
        pyxel.cls(8)
        pyxel.text(max_x//2-8,max_y//2-8,"GAME OVER", 0)
        pyxel.text(max_x//2-len(str(self.score))*2,max_y//2,"SCORE ="+str(self.score), 0)
        pyxel.rectb(max_x//2-8,max_y//2+8,36,10,0)
        pyxel.text(max_x//2-6,max_y//2+10,"NEW GAME",0)
        pyxel.mouse(True)

    def draw_victoire(self):
        """Affichage du contexte de game over"""
        pyxel.text(max_x // 2 - 8, max_y//2, "VICTORY!!!", 10) ##Affichage du message de victoire
        pyxel.rect(max_x//2-8,max_y//2+9,32,1,10) ##Rectangle pour souligner
        for i in range(0, max_y - min_y, 16):
            pyxel.blt(max_x-min_x,min_y+i,0,16,56,16,16,0) ## Affichage de la ligne d'arrivée
        pyxel.blt(2,64,0,8,80,32,32,0) ##Affichage du coeur de fin


class Player:
    def __init__(self,x,y):
        """
        :param x: coordonnées x initiales
        :param y: coordonnées y initiales
        """
        self.pv = 10  # Points de vie du joueur
        self.x = x
        self.y = y
        self.bouteilles=0 #Nombres de bouteilles de save
        self.touche=False #Détermine si le joueur est touché ou non
        self.direction="Haut"
        self.victoire=False ##Utilisé lors de la victoire


    def move(self,x,y):
        """
        Déplacements du joueur ( ne peut pas bouger si touché)
        :param x: valeur x, négatif si à gauche
        :param y: valeur y, négatif si en haut
        """
        if self.victoire: ##Peut sortir du cadre de jeu lors de la victoire
            if 0<=self.x+x<=256-14:
                self.x += x
            if 0<=self.y+y<=128-12:
                self.y += y
        else: ##Limité au cadre de jeu
            if min_x<=self.x+x<=max_x-14 and not self.touche:
                self.x+=x
            if min_y<=self.y+y<=max_y-12 and not self.touche:
                self.y+=y

    def bouteille(self):
        """Utilise un bouclier (anciennement bouteille de survie)"""
        if self.bouteilles>0 and not self.touche:
            self.touche=True
            self.bouteilles-=1
            pyxel.play(0,4)

    def tir(self):
        pyxel.play(0,5)
        if self.direction=="Droite":
            return Missile(self.x+6,self.y+6,self.direction)
        elif self.direction=="Gauche":
            return Missile(self.x,self.y+6,self.direction)
        elif self.direction=="Bas":
            return Missile(self.x+6,self.y+5,self.direction)
        else:
            return Missile(self.x+6,self.y,self.direction)

    def draw(self):
        """
        Affichage du joueur
        """
        if self.direction=="Haut":
            if self.touche:
                pyxel.blt(self.x, self.y, 0, 32, 24, 16, 16, 0)
            else:
                pyxel.blt(self.x, self.y, 0, 0, 24, 16, 16, 0)
        if self.direction=="Bas":
            if self.touche:
                pyxel.blt(self.x, self.y, 0, 32, 40, 16, 16, 0)
            else:
                pyxel.blt(self.x, self.y, 0, 0, 40, 16, 16, 0)
        if self.direction=="Droite":
            if self.touche:
                pyxel.blt(self.x, self.y, 0, 48, 40, 16, 16, 0)
            else:
                pyxel.blt(self.x, self.y, 0, 16, 40, 16, 16, 0)
        if self.direction=="Gauche":
            if self.touche:
                pyxel.blt(self.x, self.y, 0, 48, 24, 16, 16, 0)
            else:
                pyxel.blt(self.x, self.y, 0, 16, 24, 16, 16, 0)


class Rayon:
    def __init__(self,x,y,type):
        """
        :param x: coordonnées x
        :param y: coodronnées y
        :param type: type de rayon
        """
        self.x=x
        self.y=y
        self.type=type
        self.etat=False ##Etat du rayon
        self.timer=0 ## Durée du rayon

    def move(self):
        """
        Mouvement du rayon si le type est valide
        """
        if self.type==4:
            self.y-=0.25
        elif self.type==5:
            self.x-=0.25


    def draw(self):
        """
        Affichage du rayon selon le type et l'état
        """
        if self.etat:
            if self.type==0 or self.type==4:
                for i in range(0, max_x - min_x, 8):
                    pyxel.blt(self.x+i, self.y,0, 8, 0, 8, 8, 0)
            if self.type==1 or self.type==5:
                for i in range(0, max_y - min_y, 8):
                    pyxel.blt(self.x, self.y+i,0, 16, 0, 8, 8, 0)
        else:
            if self.type ==0 or self.type==4:
                for i in range(0,max_x-min_x,8):
                    pyxel.blt(self.x+i, self.y,0, 8, 8, 8, 8, 0)

            if self.type == 1 or self.type==5:
                for i in range(0, max_y - min_y, 8):
                    pyxel.blt(self.x, self.y+i,0, 16, 8, 8,8, 0)


class Coeur:
    def __init__(self,x,y,etat,bonus=None):
        """
        Permet de définir l'affichage des coeurs
        :param x: coordonnées
        :param y: coordonnées
        :param x: Etat du coeur
        """
        self.x=x
        self.y=y
        self.etat=etat
        self.bonus=bonus

    def draw(self):
        """Affichage du coeur selon le type et l'état"""
        if self.etat:
            if self.bonus:
                pyxel.blt(self.x,self.y,0,0,16,8,8,0)
            else:
                pyxel.blt(self.x, self.y,0,0,0,8,8,0)
        else:
            if self.bonus:
                pyxel.blt(self.x,self.y,0,16,16,8,8,0)
            else:
                pyxel.blt(self.x,self.y,0,8,16,8,8,0)



class Collectible:
    def __init__(self,x,y,type):
        """
        Entitées autre que rayon
        :param x: coordonnées x
        :param y: coordonnées y
        """
        self.x=x
        self.y=y
        self.type=type
        self.timer=0

    def draw(self):
        """Affichage du collectible"""
        if self.type==2:
            pyxel.blt(self.x,self.y,0,64,24,16,16,0)
        elif self.type==3:
            pyxel.blt(self.x, self.y, 0, 64, 40, 16, 16, 0)
        elif self.type==6:
            pyxel.blt(self.x,self.y,0,0,56,16,16,0)

    def move(self):
        """Déplacement du collectible"""
        self.x-=0.5

class Missile:
    def __init__(self,x,y,direction):
        """
        CA VA PETER
        (tirs du joueur)
        :param x: coordonnées x initiales
        :param y: coordonnées y initiales
        :param direction: direction du missile
        """
        self.x=x
        self.y=y
        self.direction=direction

    def move(self):
        """Déplacement du missile selon la direction"""
        if self.direction=="Droite":
            self.x+=2
        elif self.direction=="Gauche":
            self.x-=2
        elif self.direction=="Bas":
            self.y+=2
        else:
            self.y-=2

    def draw(self):
        """Affichage du missile"""
        if self.direction=="Droite" or self.direction=="Gauche":
            pyxel.blt(self.x,self.y,0,40,0,8,8,0)
        else:
            pyxel.blt(self.x,self.y,0,40,16,8,8,0)


App()
