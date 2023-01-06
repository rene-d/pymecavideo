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
from PyQt5.QtGui import QEvent

from collections import OrderedDict

from vecteur import vecteur

class Pointage(QObject):
    """
    Une classe pour représenter les pointages : séquences éventuellement
    creuses, de quadruplets (date, désignation d'objet, vecteur)

    self.data y est un dictionaire ordonné, qui a pour clés des dates 
    croissantes ; chaque date renvoie  un dictionnaire de type
    désignation d'objet => vecteur.

    self.suivis est une liste limitative de désignations d'objets

    self.deltaT est l'intervalle de temps entre deux images d'une vidéo
    """
    def __init__(self):
        QObject.__init__(self)
        self.data   = None
        self.suivis = None
        self.deltaT = None

    def dimensionne(self, n_suivis, deltaT, n_images):
        """
        Crée les structures de données quand on en connaît par avance
        le nombre
        @param n_suivis le nombre d'objets à suivre par pointage
        @param deltaT l'intervalle de temps
        @param n_images le nombre d'images de la vidéo étudiée
        """
        self.suivis = list(range(1, n_suivis+1)) # nombres 1, 2, ...
        self.deltatT = deltaT
        self.data = OrderedDict()
        for index in range(n_images):
            # crée une structure avec pour chaque date, un dictionnaire
            # désignation d'objet => vecteur ; les vecteurs sont initialement
            # indéfinis (représentés par None)
            self.data[index*deltaT] = {self.suivis[index]: None}
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
        if index is None and data is None:
            raise Exception(
                "index et date tous deux inconnus pour Pointage.pointe")
        if isinstance(position, QEvent):
            position = vecteur(position.x(), position.y()
        if index:
            date = index * self.deltaT
        self.data[data][objet] = position
        return

    def position(self, objet, index=None, date=None):
        """
        ajoute un pointage aux données ; on peut soit préciser l'index
        et la date s'en déduit, soit directement la date
        @param objet la désignation d'un objet suivi ; couramment : un nombre
        @param index s'il est donné la date est index * self.deltaT
        @param date permet de donner directement la date ; l'index reste
          prioritaire

        @return un vecteur : position de l'objet à la date donnée
        """
        if index is None and data is None:
            raise Exception(
                "index et date tous deux inconnus pour Pointage.position")
        if index:
            date = index * self.deltaT
        return self.data[date][objet]

    def trajectoire(self, objet, mode="liste"):
        """
        @param objet la désignation d'un objet suivi ; couramment : un nombre
        @param mode "liste" ou "dico" ("liste" par défaut)
        @return une liste de vecteurs (ou None quand la position est inconnue)
          les mode = "liste", sinon un dictionnaire date=>vecteur
        """
        if mode == "liste":
            return [self.data[t][objet] for t in self.data]
        return {t: self.data[t][objet] for t in self.data}

    def __str__(self):
        """
        renvoie self.data sous une forme acceptable (CSV)
        """
        result=""
        for t in self.data:
            ligne = [f"{t:.3f}"]
            for o in self.suivis:
                               
                ligne.append("{self.data[t][o].x:.3f}")
                               f"{self.data[t][o].y:.3f}"
                )
            result.append(";".join(liste))    
        return result
    

