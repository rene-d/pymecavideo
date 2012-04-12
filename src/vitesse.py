#-*- coding: utf-8 -*-

"""
    vitesse.py, a module for pymecavideo:
      a program to track moving points in a video frameset
      
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
from PyQt4.QtCore import *
from PyQt4.QtGui import *

from math import sqrt, acos, asin, pi, cos, sin, atan2
from vecteur import vecteur

class Vitesse(QLabel):
    def __init__(self, parent, point,vitesse, color, ech_v):
        """
        affiche un vecteur vitesse. Les données sont :
        parent  : le widget dont dépend le nouveau dessin
        point   : un vecteur pour l'origine
        vitesse : autre vecteur
        color   : la couleur du trait
        ech_v   : un flottant : échelle en pixel pour 1 m/s
        """
        QLabel.__init__(self, parent)
        self.color=color
        self.origine=point
        # règle le cas où on utilise une virgule comme symbole décimal
        ech=float(ech_v.replace(",","."))
        self.v=vitesse.norme()*ech
        self.angle=vitesse.anglePolaire()
        self.setGeometry(QRect(0,0,640,480))

    def paintEvent(self,event):
	if self.v!=0 : #si la vitesse est nuelle, ne l'affiche pas
	    self.painter = QPainter()
            self.painter.begin(self)
            self.painter.setPen(QColor(self.color))
            p1=QPoint(0,0)
            p2=QPoint(10*self.v,0)
            p3=QPoint(10*self.v-15,-4)
            p4=QPoint(10*self.v-15,4)
            self.painter.translate(self.origine.x(), self.origine.y())
            self.painter.rotate(self.angle*180/pi)
            self.painter.drawPolyline(p1,p2,p3,p4,p2)
            self.painter.end()
        


