#-*- coding: utf-8 -*-

"""
    point.py, a module for pymecavideo:
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
from vitesse import Vitesse

class label_numero(QLabel):
    def __init__(self, text, parent, point):
        QLabel.__init__(self, text,parent)
        self.setGeometry(point.x(), point.y(), 30, 15)
        self.setMouseTracking(True) 
    def mouseMoveEvent(self, event):
        event.ignore()
    def mouseReleaseEvent(self, event):
        event.ignore()

class Point(QLabel):
    def __init__(self, parent, point, color, numero, app, pred=None, showVelocity=True):
        """
        Le constructuer crée un point graphique.
        @param parent widget parent
        @param point coordonnées (de type vecteur)
        @param color couleur
        @param numero numéro à afficher
        @param app l'application qui commande
        @param pred le point prédecesseur
        @param showVelocity montre les vitesses
        """
        QLabel.__init__(self, parent)
        self.app=app
        self.point, self.color = point,color
        self.setGeometry(QRect(0,0,640,480))
        self.numero=label_numero("<font color='%s'>%s</font>" %(color,numero),self,point)
        self.vitesse=None
        self.succ=None     # le successeur
        self.pred=pred
        self.setMouseTracking(True)
        if pred != None:
            pred.succ = self
            pred.calcule_vitesse(self.app.ui.echelle_v.currentText(),showVelocity)
########empeche le widget de capturer les signaux, que l'on récupère dans label_video
    def mouseMoveEvent(self, event):
        event.ignore()

########empeche le widget de capturer les signaux, que l'on récupère dans label_video
    def mouseReleaseEvent(self, event):
        event.ignore()


    def montre_vitesse(self, showVelocity):
        """
        montre ou cache la vitesse, selon le paramètre showVelocity
        """
        if self.vitesse != None:
            if showVelocity:
                self.vitesse.show()
            else:
                self.vitesse.hide()
        
    def calcule_vitesse(self, ech, showVelocity=True):
        """
        si self.pred et self.succ sont tous deux définis, le calcul de
        vitesse est possible. Le vecteur vitesse précédent éventuel est effacé
        et un nouveau est tracé.
        Paramètres :
        ech : l'échelle en px pour 1m/s, type chaîne de caractères
        showVelocity : booléen, vrai si on doit montrer la vitesse tout de suite
        """
        if self.vitesse != None:
            self.vitesse.hide()
            del self.vitesse
        if self.pred != None and self.succ != None:
            deltaP = self.succ.point - self.pred.point
            v=deltaP*(1/(2*self.app.deltaT))*self.app.echelle_image.mParPx()
            self.vitesse=Vitesse(self,self.point,v, self.color, ech)
            if showVelocity:
                self.vitesse.show()
            
    def paintEvent(self,event):
        self.painter = QPainter()
        self.painter.begin(self)
        self.painter.setPen(QColor(self.color))
        self.painter.translate(self.point.x(), self.point.y())
        self.painter.drawLine(-2,0,2,0)
        self.painter.drawLine(0,-2,0,2)
        self.painter.end()
    def showVec(self):
        if self.app.prox and self.vitesse: self.vitesse.show()
    def hideVec(self):
        if self.app.prox and self.vitesse: self.vitesse.hide()


class Repere(Point):
    def __init__(self, parent, point, color, numero, app):
        Point.__init__(self,parent, point, color, numero, app)
    def paintEvent(self,event):
        self.painter = QPainter()
        self.painter.begin(self)
        self.painter.setPen(QColor(self.color))
        self.painter.translate(self.point.x(), self.point.y())
        p1=QPoint(self.app.sens_X*(-20),0)
        p2=QPoint(self.app.sens_X*(20),0)
        p3=QPoint(self.app.sens_X*(18),1)
        p4=QPoint(self.app.sens_X*(18),-1)
        self.painter.scale(8,8)
        self.painter.drawPolyline(p1,p2,p3,p4,p2)
        self.painter.rotate(self.app.sens_X*self.app.sens_Y*(-90))
        self.painter.drawPolyline(p1,p2,p3,p4,p2)
        self.painter.end()
    def mouseMoveEvent(self, event):
        event.ignore()
