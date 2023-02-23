# -*- coding: utf-8 -*-
"""
    vecteur.py is a module of pymecavideo.
    pymecavideo is a program to track moving points in a video frameset
    Copyright (C) 2007 Jean-Baptiste Butet <ashashiwa@gmail.com>

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

"""
vecteur.py implements some operations for 2D vectors, using tuples
"""




import math

from PyQt6.QtCore import QPointF

class vecteur:
    """
    une classe pour des vecteurs 2D ; les coordonnées sont flottantes, et
    on peut accéder à celles-ci par les propriétés self.x et self.y

    Paramètres du constructeur

    @param x une abscisse, nulle par défaut
    @param y une ordonnée, nulle par défaut
    @param qPoint (None par défaut) ; si ce paramètre est d'un type
      qui possède les méthodes .x() et .y(), il sert à créer le vecteur
      de façon prioritaire.
    @param precision permet de donner la précision qu'on souhaite (nombre
      de chiffre significatifs). None par défaut, ce qui implique
      4 chiffre significatifs
    """
    def __init__(self, x=0, y=0, qPoint=None, precision = None):
        if qPoint:
            self.value = (qPoint.x(), qPoint.y())
            return
        self.precision = 4 if precision is None else precision
        self.value = (self.signif(float(x), self.precision),
                      self.signif(float(y), self.precision))
        return
    
    def copy(self):
        return vecteur(self.x, self.y)

    @property
    def x(self):
        return self.value[0]

    @property
    def y(self):
        return self.value[1]

    def manhattanLength(self):
        """
        @return la longueur « de mahattan »
        """
        return abs(self.x) + abs(self.y)
    
    def miroirY(self):
        """
        change le signe de l'ordonnée ; utile comme l'axe y de l'écran
        est dirigé vers le bas.
        """
        self.value = (self.value[0], - self.value[1])
        return
    
    def redresse(self, video):
        """
        ajuste les signes des coordonnées
        @param video un objet qui a les propriétés sens_X et sens_Y (+-1)
        """
        self.value = (video.sens_X * self.value[0],
                      - video.sens_Y * self.value[1])
        return
    
    def __getitem__(self, i):
        # print "Utilisation de vecteur.__getitem__ déconseillée"
        return self.value[i]

    def setValue(self, x=None, y=None):
        if x == None:
            x = self.value[0]
        if y == None:
            y = self.value[1]
        self.value = (self.signif(float(x), self.precision),
                      self.signif(float(y), self.precision))

    def rounded(self):
        self.value = (math.floor(
            self.value[0] + 0.5), math.floor(self.value[1] + 0.5))

    def __add__(self, v):
        x = self.x + v.x
        y = self.y + v.y
        return vecteur(x, y)

    def __eq__(self, v):
        return v is not None and self.x == v.x and self.y == v.y
    
    def __sub__(self, v):
        x = self.x - v.x
        y = self.y - v.y
        return vecteur(x, y)

    def __mul__(self, v):
        if type(v) == type(self):
            # produit scalaire de deux vecteurs
            return self.x * v.x + self.y + v.y
        else:
            # produit du vecteur par un nombre
            x = float(v) * self.x
            y = float(v) * self.y
            return vecteur(self.signif(x, self.precision), self.signif(y, self.precision))

    def __str__(self):
        return "(%5f, %5f)" % (self.x, self.y)

    def toIntStr(self):
        return f"({round(self.x)}, {round(self.y)})"
    
    def __repr__(self):
        return "vecteur %s" % self

    @property
    def norme(self):
        return math.sqrt(self.x * self.x + self.y * self.y)

    @property
    def rounded(self):
        return vecteur(round(self.x), round(self.y))

    @property
    def anglePolaire(self):
        return math.atan2(self.y, self.x)

    def minXY(self, v):
        if v == None:
            return self
        else:
            if self.x > v.x:
                x = v.x
            else:
                x = self.x
            if self.y > v.y:
                y = v.y
            else:
                y = self.y
            return vecteur(x, y)

    def maxXY(self, v):
        if v == None:
            return self
        else:
            if self.x < v.x:
                x = v.x
            else:
                x = self.x
            if self.y < v.y:
                y = v.y
            else:
                y = self.y
            return vecteur(x, y)

    def rotate(self, angle, largeur, hauteur):
        x1, y1 = self.x, self.y
        if angle % 360 == 90:
            return vecteur(hauteur-y1, x1)
        elif angle % 360 == 270:
            return vecteur(y1, largeur-x1)
        elif angle % 360 == 0:
            return vecteur(x1, y1)
        elif angle % 360 == 180:
            return vecteur(-x1, -y1)

    def signif(self, x, digit):
        if x == 0:
            return 0
        return round(x, digit - int(math.floor(math.log10(abs(x)))) - 1)

    def homothetie(self, ratio):
        return vecteur(self.x*ratio, self.y*ratio)

    def toQPointF(self):
        """
        transformation en QPointF
        """
        return QPointF(self.x, self.y)
