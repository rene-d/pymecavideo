#-*- coding: utf-8 -*-
"""
    echelle, a module for pymecavideo:
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

from vecteur import vecteur

from math import sqrt
from PyQt4.QtCore import *
from PyQt4.QtGui import *

class echelle(QObject):
    def __init__(self, p1=vecteur(0,0), p2=vecteur(0,0)):
        self.p1,self.p2 = p1, p2
        self.longueur_reelle_etalon = 1
        self.longueur_pixel_etalon = 1
    
    def calcul_longueur_pixels(self, p1, p2):
        v=p1-p2
        return  v.norme()
    
    def mParPx(self):
        """renvoie le nombre de mètre par pixel"""
        return self.longueur_reelle_etalon/self.longueur_pixel_etalon
    
    def applique_echelle(self,pos):
        """
        les positions pos sont en pixels, ça renvoie une liste
        de positions (vecteurs) en mètre.
        """
        result=[]
        for p in pos:
            result.append((vecteur(0,480) - p)*self.mParPx())
        return result

class Label_Echelle(QLabel):
    def __init__(self, parent,app):
        QLabel.__init__(self, parent)
        self.parent = parent
        self.setGeometry(QRect(10,60,640,480))
        self.setAutoFillBackground(False)
        self.p1=vecteur()
        self.p2=vecteur()
        self.app = app
        self.setCursor(Qt.CrossCursor)
        
    def mousePressEvent(self, event):
        if event.button() != 1:
            self.p1=vecteur(-1,-1)
            self.close()
        self.p1 = vecteur(event.x(),event.y())
    
    def paintEvent(self, event):
        painter = QPainter()
        painter.begin(self)
        #painter.drawPixmap(0,0,self.pix)
	painter.setPen(Qt.red)
        if self.p1.x() >= 0:
	    painter.drawLine(self.p1.x(), self.p1.y(), self.p2.x(), self.p2.y())
        painter.end()
    
    def mouseMoveEvent(self, event):
        self.p2 = vecteur(event.x() + 1, event.y() + 1)
        self.update()
        
        
    def mouseReleaseEvent(self, event):
        if event.button() == 1 and self.p1.x() >= 0:
            self.p2 = vecteur(event.x() + 1, event.y() + 1)
        
        
        self.parent.index_du_point=0
        
        self.app.echelle_image.p1=self.p1.copy()
        self.app.echelle_image.p2=self.p2.copy()
        self.app.p1=self.p1.copy()
        self.app.p2=self.p2.copy()
        self.app.echelle_image.longueur_pixel_etalon = self.app.echelle_image.calcul_longueur_pixels(self.p1, self.p2)
        epxParM=self.app.echelle_image.longueur_pixel_etalon/self.app.echelle_image.longueur_reelle_etalon
        self.app.ui.echelleEdit.setText("%.1f" %epxParM)
        self.parent.echelle_definie=True
        self.app.ui.spinBox_nb_de_points.setEnabled(1)
        self.app.mets_a_jour_label_infos(u"""Choisir le nombre de points puis "Démarrer l'acquisition" """)
        self.app.ui.Bouton_lance_capture.setEnabled(1)
        self.app.feedbackEchelle()
            
        self.close()
    
