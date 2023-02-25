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

from PyQt6.QtCore import QObject
from PyQt6.QtGui import QMouseEvent

from vecteur import vecteur
from echelle import echelle

from collections import deque

class Pointage(QObject):
    """
    Une classe pour représenter les pointages : séquences éventuellement
    creuses, de quadruplets (date, désignation d'objet, vecteur)
    """
    def __init__(self):
        QObject.__init__(self)
        self.init_pointage()
        return

    def init_pointage(self):
        """
        self.data y est un dictionaire ordonné, qui a pour clés des dates 
        croissantes ; chaque date renvoie  un dictionnaire de type
        désignation d'objet => vecteur.

        self.suivis est une liste limitative de désignations d'objets

        self.deltaT est l'intervalle de temps entre deux images d'une vidéo

        self.echelle est l'échelle en px par mètre

        """
        self.data    = None             # les données de pointage
        self.dates   = None             # liste des index temporels
        self.suivis  = None             # la liste des objets mobiles suivis
        self.deltaT  = None             # intervalle de temps entre deux images
        self.echelle = None             # pixels par mètre
        self.origine = None             # position de l'origine sur les images
        self.echelle_image = echelle()  # objet gérant l'échelle
        self.sens_X = 1                 # sens de l'axe des abscisses
        self.sens_Y = 1                 # sens de l'axe des ordonnées
        self.defaits = deque()          # pile des pointages défaits
        return

    def defaire(self):
        """
        retire le dernier pointage de self.data et l'empile dans
        self.defaits
        """
        der = self.derniere_image()
        if der:
            t = self.dates[der - 1]
            self.defaits.append(self.data[t])
            self.data[t] = {obj: None for obj in self.suivis}
        return

    def refaire(self):
        """
        dépile un pointage de self.defaits et le rajoute à la fin de
        self.data
        """
        if len (self.defaits) > 0:
            der = self.derniere_image()
            if der and der < self.image_max:
                t = self.dates[der]
            else:
                t = self.dates[0]
            pointage = self.defaits.pop()
            self.data[t] = pointage
        return

    def peut_defaire(self):
        """
        @return vrai si on peut défaire un pointage
        """
        return bool(self.derniere_image())

    def peut_refaire(self):
        """
        @return vrai si on peut refaire un pointage
        """
        return len(self.defaits) > 0
    
    def purge_defaits(self):
        """
        purge les données à refaire si
        on vient de cliquer sur la vidéo pour un pointage
        """
        self.defaits = deque()
        return

    
    def clearEchelle(self):
        """
        oublie la valeur de self.echelle_image
        """
        self.echelle_image = echelle()
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
            position = vecteur(qPoint = position.position())
        elif isinstance(position, vecteur):
            pass
        else:
            raise Exception("dans Pointage.pointe, la position est soit QMouseEvent, soit vecteur")
        if index is not None:
            date = index * self.deltaT
        if date not in self.data:
            raise Exception(f"date incorrecte dans Pointage.pointe : {date}")
        self.data[date][objet] = position
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
        
    def __str__(self):
        return self.csv_string()

    def __len__(self):
        if self.dates is not None:
            return len(self.dates)
        return 0

    def __bool__(self):
        """
        @return faux si toutes les pointages sont None
        """
        if self.dates is None or not self.suivis:
            return False
        for t in self.dates:
            if self.data[t][self.suivis[0]] is not None:
                return True
        return False
            
    def premiere_image(self):
        """
        donne le numéro de la première image pointée (1 au minimum),
        ou None si aucun pointage n'est fait
        """
        for i, t in enumerate(self.dates):
            if self.data[t][self.suivis[0]] is not None:
                return i + 1
        return None
    
    def derniere_image(self):
        """
        donne le numéro de la dernière image pointée (on compte à partir de 1),
        ou None si aucun pointage n'est fait
        """
        for i, t in zip(list(range(len(self.dates))[::-1]), self.dates[::-1]):
            if self.data[t][self.suivis[0]] is not None:
                return i + 1
        return None
    
    def csv_string(self, sep =";", unite="px", debut=1, origine=vecteur(0,0)):
        """
        renvoie self.data sous une forme acceptable (CSV)
        @param sep le séparateur de champ, point-virgule par défaut.
        @param unite l'unité du vecteur position : peut être "px" pour pixel
          (par défaut) ou "m" pour mètre
        @param debut la première image qui a été pointée
        @param origine un vecteur pour l'origine du repère ; (0,0) par défaut
        """
        if unite == "px":
            mul =1
        elif unite == "m":
            mul = self.echelle_image.mParPx()
        else:
            raise Exception(f"dans Pointage.trajectoire, unité illégale {unite}")

        result=[]
        en_tete = ["t"]
        for o in self.suivis:
            en_tete.append(f"x{o}")
            en_tete.append(f"y{o}")
        result.append(sep.join(en_tete))
        dates = list(self.data.keys())    # toutes les dates
        dates_pointees = dates[debut-1:]  # dates qui commencent au début du pointage
        dd = zip(dates, dates_pointees)   # zip des deux listes précédentes
        for t, t_point in list(dd) :
            # l'itération ne commence qu'à la première image pointée
            # t est une date qui commence à zéro
            # t_point commence au premier pointage
            ligne = [f"{t:.3f}"]
            for o in self.suivis:
                if self.data[t_point][o] is not None:
                    ligne.append(f"{self.sens_X   * (self.data[t_point][o].x - origine.x) * mul:4g}")
                    ligne.append(f"{- self.sens_Y * (self.data[t_point][o].y - origine.y) * mul:4g}")
            result.append(sep.join(ligne))
        result.append("") # pour finir sur un saut de ligne
        return "\n".join(result)
    
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

    def une_trajectoire(self, obj):
        """
        renvoie la séquence de positions d'un objet pointé (seulement là
        où il a été pointé, ni avant, ni après)
        @param obj un des objets mobiles pointés
        @return une liste [instance de vecteur, ...]
        """
        return [self.data[t][obj] for t in self.dates if self.data[t][obj]]

    def les_trajectoires(self):
        """
        renvoie un dictionnaire objet => trajectoire de l'objet
        @return { objet: [instance de vecteur, ...], ...}
        """
        return {obj: self.une_trajectoire(obj) for obj in self.suivis}

    def index_trajectoires(self, debut = 1):
        """
        renvoie la liste des numéros des images pointés au long des
        trajectoire. N.B. : la première image d'un film est numérotée 1
        @param debut permet de choisir le numéro de la toute première image
          du film (1 par défaut)
        """
        return [i + debut for i,t in enumerate(self.dates)
                if self.data[t][self.suivis[0]]]

    def pointEnMetre(self, p):
        """
        renvoie un point, dont les coordonnées sont en mètre, dans un
        référentiel "à l'endroit"
        @param p un point en "coordonnées d'écran"
        """
        self.dbg.p(2, "rentre dans 'pointEnMetre'")
        if p is None: return None
        return vecteur(
            self.sens_X * (p.x - self.origine.x) * self.echelle_image.mParPx(),
            self.sens_Y * (self.origine.y - p.y) * self.echelle_image.mParPx())

    def liste_t_pointes(self):
        """
        renvoie la liste des dates où on a pointé des positions
        @return une liste [float, ...]
        """
        return [t for t in self.dates
                if self.data[t][self.suivis[0]] is not None]

    def liste_pointages(self, obj=None):
        """
        renvoie la liste des pointages pour un objet
        @param obj désigne l'objet choisi; si obj est None, 
          c'est le premier des objets
        """
        if obj is None: obj = self.suivis[0]
        return [self.data[t][obj] for t in self.dates
                if self.data[t][obj] is not None]
    
    @property
    def nb_obj(self):
        """
        @return le nombre d'objets suivis
        """
        if self.suivis is None: return 0
        return len(self.suivis)

    def gen_iter_TOP(self):
        """
        générateur pour accéder aux données
        @return un itérateur qui renvoie à chaque appel
          i, t, iter_OP, où i et t sont une énumération des dates
          et iter_OP est un itérateur pour accéder aux données au temps t.

          Quand on parcourt iter_OP, il renvoie j, obj, P où j et
          obj sont une énumération de self.suivis et le point P
          est un vecteur qui correspond au temps t et à l'objet obj.
        """
        return ((i, t, ((j, obj, self.data[t][obj]) \
                         for j, obj in enumerate(self.suivis))) \
                 for i, t in enumerate(self.dates))
    
    def gen_iter_TOPV(self):
        """
        genérateur pour accéder aux données
        @yield i, t, iter_OPV où i et t sont une énumération des dates
          et iter_OPV est un itérateur pour accéder aux données au temps t.

          Quand on parcourt iter_OPV, il renvoie j, obj, P, V où j et
          obj sont une énumération de self.suivis, le point P
          est un vecteur qui correspond au temps t et à l'objet obj,
          et la vitesse V (quand elle est évaluable) est l'intervalle
          entre le point P et celui qui le précède dans le temps, divisé
          par l'intervalle de temps.
        """
        i = 0
        points_avant = [None] * len(self.suivis)
        while i < len (self.dates):
            t = self.dates[i]
            
            def vitesse(p2, p1):
                """
                vitesse du point p2
                @param p2 position d'un objet
                @param p1 position du même objet juste avant dans le temps
                """
                if p1 and p2:
                    return (p2-p1) * (1/self.deltaT)
                return None
            
            yield i, t, ((j, obj, self.data[t][obj], vitesse(self.data[t][obj], points_avant[j])) \
                         for j,obj in enumerate(self.suivis))
            points_avant = [self.data[t][obj] for obj in self.suivis]
            i = i + 1
        return
    
    def gen_iter_traj(self, obj):
        """
        renvoie un itérateur sur la trajectoire d'un objet
        @param obj un objet suivi
        @return un itérateur qui renvoie chacun des points de la trajectoire
          de l'objet obj.
        """
        return (self.data[t][obj] for t in self.dates)

    def gen_iter_OP(self):
        """
        générateur pour accéder aux données
        @yield i, obj, iter_P où i et obj viennent d'une eénumération
          des objets, et iter_P un itérateur qui permet de parcourir
          la trajectoire de l'objet courant.
        """
        return ((i, obj, self.gen_iter_traj(obj)) \
                for i, obj in enumerate(self.suivis))
