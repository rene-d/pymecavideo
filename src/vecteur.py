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
class vecteur:
    def __init__(self, x=0, y=0):
        self.precision = 4  # nb de  chiffres significatifs
        self.value = (self.signif(float(x), self.precision),
                      self.signif(float(y), self.precision))

    def copy(self):
        return vecteur(self.x, self.y)

    @property
    def x(self):
        return self.value[0]

    @property
    def y(self):
        return self.value[1]

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

    def __repr__(self):
        return "vecteur %s" % self

    def norme(self):
        return math.sqrt(self.x * self.x + self.y * self.y)

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
        if angle == 90:

            return vecteur(hauteur-y1, x1)
        elif angle == -90:
            return vecteur(y1, largeur-x1)
        elif angle == 0:
            return vecteur(x1, y1)
        elif angle == 0:
            return vecteur(x1, y1)
        elif angle == 180:
            return vecteur(-x1, -y1)

    def signif(self, x, digit):
        if x == 0:
            return 0
        return round(x, digit - int(math.floor(math.log10(abs(x)))) - 1)

    def homothetie(self, ratio):
        return vecteur(self.x*ratio, self.y*ratio)
