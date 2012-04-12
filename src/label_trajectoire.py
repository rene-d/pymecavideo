#-*- coding: utf-8 -*-
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from vecteur import vecteur

class Label_Trajectoire(QLabel):
    def __init__(self, parent, app, origine = vecteur(0,0), referentiel = 0):
        QLabel.__init__(self,parent)
        self.app=app
        self.setGeometry(QRect(0,0,640,480))
        self.setCursor(Qt.ArrowCursor)
        self.setAutoFillBackground(True)
        self.setMouseTracking(1)
        self.couleurs=["red", "blue", "cyan", "magenta", "yellow", "gray", "green"]
        self.origine = origine
        self.referentiel = referentiel

    def mouseMoveEvent(self, event):
        self.app.traiteSouris(event.pos())
    
    def paintEvent(self,event):
        self.painter = QPainter()
        self.painter.begin(self)
        self.painter.fillRect(QRect(0,0,640,480),QColor("grey"))
        for points in self.app.points.values() :
            color=0
            for point in points:
                if self.referentiel !=0:
                    ptreferentiel = points[int(self.referentiel)]

                else :
                    ptreferentiel = vecteur(0,0)
                if type(point)!= type(""): 
                    self.painter.setPen(QColor(self.couleurs[color]))
                    self.painter.setFont(QFont("", 10))
                    self.painter.translate(point.x()+self.origine.x()-ptreferentiel.x(), point.y()+self.origine.y()-ptreferentiel.y())

                    self.painter.drawLine(-2,0,2,0)
                    self.painter.drawLine(0,-2,0,2)
                    self.painter.translate(-10, +10)
                    self.painter.drawText(0,0,str(color+1))
                    self.painter.translate(-point.x()-self.origine.x()+ptreferentiel.x()+10, -point.y()-10-self.origine.y()+ptreferentiel.y())
                    color+=1

        
        self.painter.end()
        
