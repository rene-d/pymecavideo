# -*- coding: utf-8 -*-

"""
    pointage, a module for pymecavideo:
      a program to track moving points in a video frameset
      
    Copyright (C) 2023 Georges Khaznadar <georgesk@debian.org>

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from PyQt5.QtCore import QObject
from PyQt5.QtGui import QMouseEvent

from vecteur import vecteur
from collections import deque

class Pointage(QObject):
    """
    Une classe pour représenter les pointages : séquences éventuellement
    creuses, de quadruplets (date, désignation d'objet, vecteur)

    self.data y est un dictionaire ordonné, qui a pour clés des dates 
    croissantes ; chaque date renvoie  un dictionnaire de type
    désignation d'objet => vecteur.

    self.suivis est une liste limitative de désignations d'objets

    self.deltaT est l'intervalle de temps entre deux images d'une vidéo

    self.echelle est l'échelle en px par mètre

    self.vide reste vrai tant qu'on n'a pas encore pointé ; modifié par
      self.pointe(...)
    """
    def __init__(self):
        QObject.__init__(self)
        self.data    = None
        self.suivis  = None
        self.deltaT  = None
        self.echelle = None
        self.vide    = True
        self.pileFaits = deque()     # pile pour mémoriser les pointages faits
        self.pileArefaire = deque()  # pile pour mémoriser les pointages défaits
        return

    def setEchelle(self, echelle):
        self.echelle = echelle
        return
    
    def dimensionne(self, n_suivis, deltaT, n_images):
        """
        Crée les structures de données quand on en connaît par avance
        le nombre
        @param n_suivis le nombre d'objets à suivre par pointage
        @param deltaT l'intervalle de temps
        @param n_images le nombre d'images de la vidéo étudiée
        """
        self.suivis = list(range(1, n_suivis+1)) # nombres 1, 2, ...
        self.deltaT = deltaT
        self.dates = [deltaT * i for i in range(n_images)]
        self.data = {}
        self.vide = True
        for index in range(n_images):
            # crée une structure avec pour chaque date, un dictionnaire
            # désignation d'objet => vecteur ; les vecteurs sont initialement
            # indéfinis (représentés par None)
            self.data[index*deltaT] = {o: None for o in self.suivis}
        return

    def pointe(self, objet, position, index=None, date=None):
        """
        ajoute un pointage aux données ; on peut soit préciser l'index
        et la date s'en déduit, soit directement la date
        @param objet la désignation d'un objet suivi ; couramment : un nombre
        @param position
        @param index s'il est donné la date est index * self.deltaT
        @param date permet de donner directement la date ; l'index reste
          prioritaire
        """
        if index is None and date is None:
            raise Exception(
                "index et date tous deux inconnus pour Pointage.pointe")
        if isinstance(position, QMouseEvent):
            position = vecteur(position.x(), position.y())
        elif isinstance(position, vecteur):
            pass
        else:
            raise Exception("dans Pointage.pointe, la position est soit QMouseEvent, soit vecteur")
        if index is not None:
            date = index * self.deltaT
        if date not in self.data:
            raise Exception(f"date incorrecte dans Pointage.pointe : {date}")
        self.data[date][objet] = position
        self.pileFaits.append((date, objet, position))
        self.vide = False
        return

    def peut_defaire(self):
        """
        @return vrai si on peut défaire un pointage
        """
        return len(self.pileFaits) > 0
    
    def defaire(self):
        """
        Permet de défaire les pointages faits précédemment
        """
        if len(self.pileFaits) > 0:
            date, objet, position = self.pileFaits.pop()
            self.pileArefaire.append((date, objet, position))
            self.data[date][objet] = None
        return

    def purge_refaire(self):
        """
        oublie les pointages à refaire
        """
        self.pileArefaire = deque()
        return

    def peut_refaire(self):
        """
        @return vrai si on peut refaire un pointage
        """
        return len(self.pileArefaire) > 0
    
    def refaire(self):
        """
        Refait un pointage si possible
        """
        if len(self.pileArefaire) > 0:
            date, objet, position = self.pileArefaire.pop()
            data[date][objet] = position
            self.pileFaits.append((date, objet, position))
        return
            
        
    def position(self, objet, index=None, date=None, unite="px"):
        """
        ajoute un pointage aux données ; on peut soit préciser l'index
        et la date s'en déduit, soit directement la date
        @param objet la désignation d'un objet suivi ; couramment : un nombre
        @param index s'il est donné la date est index * self.deltaT
        @param date permet de donner directement la date ; l'index reste
          prioritaire
        @param unite l'unité du vecteur position : peut être "px" pour pixel
          (par défaut) ou "m" pour mètre

        @return un vecteur : position de l'objet à la date donnée
        """
        if index is None and date is None:
            raise Exception(
                "index et date tous deux inconnus pour Pointage.position")
        if index is not None:
            date = index * self.deltaT
        if date not in self.dates:
            raise Exception("date incorrecte dans Pointage.pointe")
        if unite =="px":
            return self.data[date][objet]
        elif unite == "m":
            return self.data[date][objet]*(1/self.echelle)
        else:
            raise Exception(f"dans Pointage.position, unité illégale {unite}")
        
    def trajectoire(self, objet, mode="liste", unite = "px"):
        """
        @param objet la désignation d'un objet suivi ; couramment : un nombre
        @param mode "liste" ou "dico" ("liste" par défaut)
        @param unite l'unité du vecteur position : peut être "px" pour pixel
          (par défaut) ou "m" pour mètre

        @return une liste de vecteurs (ou None quand la position est inconnue)
          les mode = "liste", sinon un dictionnaire date=>vecteur
        """
        if unite == "px":
            mul =1
        elif unite == "m":
            mul = 1/self.echelle
        else:
            raise Exception(f"dans Pointage.trajectoire, unité illégale {unite}")
        if mode == "liste":
            return [self.data[t][objet]*mul for t in self.dates]
        return {t: self.data[t][objet]*mul for t in self.dates}

    def __str__(self, sep =";", unite="px"):
        """
        renvoie self.data sous une forme acceptable (CSV)
        @param sep le séparateur de champ, point-virgule par défaut.
        @param unite l'unité du vecteur position : peut être "px" pour pixel
          (par défaut) ou "m" pour mètre
        """
        if unite == "px":
            mul =1
        elif unite == "m":
            mul = 1/self.echelle
        else:
            raise Exception(f"dans Pointage.trajectoire, unité illégale {unite}")

        result=[]
        en_tete = ["t"]
        for o in self.suivis:
            en_tete.append(f"x{o}")
            en_tete.append(f"y{o}")
        result.append(sep.join(en_tete))
        for t in self.data:
            ligne = [f"{t:.3f}"]
            for o in self.suivis:
                if self.data[t][o] is not None:
                    ligne.append(f"{self.data[t][o].x * mul:.3f}")
                    ligne.append(f"{self.data[t][o].y * mul:.3f}")
            result.append(sep.join(ligne))
        result.append("") # pour finir sur un saut de ligne
        return "\n".join(result)
    
def test():
    """
    Vérification que la structure de données et OK
    """
    p = Pointage()
    p.dimensionne(3, 0.040, 5) # 3 objets, 25 images par s, 5 images
    assert(p.data == {
        0.000: {1: None, 2: None, 3: None}, 
        0.040: {1: None, 2: None, 3: None}, 
        0.080: {1: None, 2: None, 3: None}, 
        0.120: {1: None, 2: None, 3: None}, 
        0.160: {1: None, 2: None, 3: None}, 
    })
    for i in range(5):
        p.pointe(1, vecteur(i, i), index=i)
        p.pointe(2, vecteur(i, 2*i), date = i * 0.040)
    assert(p.data == {
        0.000: {1: vecteur(0,0), 2: vecteur(0,0), 3: None}, 
        0.040: {1: vecteur(1,1), 2: vecteur(1,2), 3: None}, 
        0.080: {1: vecteur(2,2), 2: vecteur(2,4), 3: None}, 
        0.120: {1: vecteur(3,3), 2: vecteur(3,6), 3: None}, 
        0.160: {1: vecteur(4,4), 2: vecteur(4,8), 3: None}, 
    })
    assert(p.position(1, date=.08) == vecteur(2,2))
    assert(p.position(2, index=3)  == vecteur(3,6))
    assert(p.trajectoire(1) == [vecteur(i,i) for i in range(5)])
    assert(p.trajectoire(2) == [vecteur(i,2*i) for i in range(5)])
    assert(p.trajectoire(2, mode="dico") == {i*.04: vecteur(i,2*i) for i in range(5)})
    p.setEchelle(50) # 50 pixels par mètre
    assert(p.trajectoire(2, mode="dico", unite="m") == {i*.04: vecteur(i/50,2*i/50) for i in range(5)})
    assert(str(p) == """\
t;x1;y1;x2;y2;x3;y3
0.000;0.000;0.000;0.000;0.000
0.040;1.000;1.000;1.000;2.000
0.080;2.000;2.000;2.000;4.000
0.120;3.000;3.000;3.000;6.000
0.160;4.000;4.000;4.000;8.000
""")
    assert(p.__str__(unite="m") == """\
t;x1;y1;x2;y2;x3;y3
0.000;0.000;0.000;0.000;0.000
0.040;0.020;0.020;0.020;0.040
0.080;0.040;0.040;0.040;0.080
0.120;0.060;0.060;0.060;0.120
0.160;0.080;0.080;0.080;0.160
""")
    return
    
if __name__ == "__main__":
    test()
