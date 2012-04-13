#-*- coding: utf-8 -*-
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from vecteur import vecteur

class Label_Trajectoire(QLabel):
    def __init__(self, parent, app, origine = vecteur(0,0), referentiel = 0):
        QLabel.__init__(self,parent)
        print "INIT"
        self.app=app
        self.setGeometry(QRect(0,0,640,480))
        self.setCursor(Qt.ArrowCursor)
        self.setAutoFillBackground(True)
        self.setMouseTracking(1)
        self.couleurs=["red", "blue", "cyan", "magenta", "yellow", "gray", "green","red", "blue", "cyan", "magenta", "yellow", "gray", "green"]
        self.origine = origine
        self.referentiel = referentiel
        self.origine_mvt=vecteur(self.geometry().width()/2,self.geometry().height()/2)
        

    def mouseMoveEvent(self, event):
        self.app.traiteSouris(event.pos())
    
    def paintEvent(self,event):
        self.painter = QPainter()
        self.painter.begin(self)
        self.painter.fillRect(QRect(0,0,640,480),QColor("grey"))
        ############################################################
        #paint the origin
        print "self.origine_mvt", self.origine_mvt
        self.painter.setPen(Qt.green)
        self.painter.drawLine(self.origine_mvt.x()-5, self.origine_mvt.y(), self.origine_mvt.x()+5, self.origine_mvt.y())
        self.painter.drawLine(self.origine_mvt.x(), self.origine_mvt.y()-5, self.origine_mvt.x(), self.origine_mvt.y()+5)
        self.painter.drawText(self.origine_mvt.x(), self.origine_mvt.y()+15, "O")
        
        
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
        ############################################################
        #paint repere
        self.painter.setPen(Qt.green)
        #self.painter.translate(0,0)
        self.painter.translate(self.origine_mvt.x(), self.origine_mvt.y())
        p1=QPoint(self.app.sens_X*(-40),0)
        p2=QPoint(self.app.sens_X*(40),0)
        p3=QPoint(self.app.sens_X*(36),2)
        p4=QPoint(self.app.sens_X*(36),-2)
        self.painter.scale(1,1)
        self.painter.drawPolyline(p1,p2,p3,p4,p2)
        self.painter.rotate(self.app.sens_X*self.app.sens_Y*(-90))
        self.painter.drawPolyline(p1,p2,p3,p4,p2)
        ############################################################
        
        self.painter.end()
        
