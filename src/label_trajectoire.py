#-*- coding: utf-8 -*-
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from math import sqrt, atan2, degrees
from vecteur import vecteur

class Label_Trajectoire(QLabel):
    def __init__(self, parent, app, origine = vecteur(0,0), referentiel = 0):
        QLabel.__init__(self,parent)
        self.app=app
        self.setGeometry(QRect(0,0,640,480))
        self.setCursor(Qt.ArrowCursor)
        self.setAutoFillBackground(True)
        self.setMouseTracking(1)
        self.couleurs=["red", "blue", "cyan", "magenta", "yellow", "gray", "green","red", "blue", "cyan", "magenta", "yellow", "gray", "green"]
        self.origine = origine
        self.referentiel = referentiel
        self.origine_mvt=vecteur(self.geometry().width()/2,self.geometry().height()/2)
        self.setMouseTracking(True)
        self.speedToDraw = ()
        

    def mouseMoveEvent(self, event):
        #self.app.traiteSouris(event.pos())
        #self.app.dbg.p(2,"in label_trajectoire, mousemoveevent")
        near=20
        #print self.app.points
        ####Look if mouse is near a point
        if self.app.ui.radioButtonNearMouse.isChecked():
            for key in self.app.points.keys() :
                points= self.app.points[key]
                for i in range(len(points)):
                    point=points[i]
                    if self.referentiel !=0:
                        ptreferentiel = points[int(self.referentiel)]

                    else :
                        ptreferentiel = vecteur(0,0)
                        
                    if type(point)!= type(""): 
                        #self.app.dbg.p(2,"distance between mouse and a point")
                        pos = event.pos()
                        distance = QPoint(point.x()+self.origine.x()-ptreferentiel.x(), point.y()+self.origine.y()-ptreferentiel.y())-pos
                        if self.app.ui.checkBoxVectorSpeed.isChecked():
                            if distance.manhattanLength() < near :
                                self.app.dbg.p(2,"mouse near a point")           
                                ##compute speed
                                
                                if key != 0:##coordonnates of n-1 and n+1 point
                                    pointBefore = QPoint(self.app.points[key-1][i].x(), self.app.points[key-1][i].y())
                                    try : 
                                        pointAfter = QPoint(self.app.points[key+1][i].x(), self.app.points[key+1][i].y())
                                        
                                        vector_speed = pointAfter-pointBefore
                                        #speed = sqrt(vector_speed.x()**2+vector_speed.y()**2)
                                        #print "DRAW",pointBefore, pointAfter,vector_speed
                                        self.speedToDraw = (QPoint(point.x(),point.y()), vector_speed,i) #i give the color
                                        self.repaint()
                                    except KeyError: #last point -> can't compute speed
                                        pass
        elif self.app.ui.radioButtonSpeedEveryWhere.isChecked():
            pass
                    
                    
        

    
    def paintEvent(self,event):
        self.painter = QPainter()
        self.painter.begin(self)
        self.painter.fillRect(QRect(0,0,640,480),QColor("grey"))
        self.painter.setRenderHint(QPainter.Antialiasing) 
        

        
        
        ############################################################
        #paint the origin
        self.painter.setPen(Qt.green)
        self.painter.drawLine(self.origine_mvt.x()-5, self.origine_mvt.y(), self.origine_mvt.x()+5, self.origine_mvt.y())
        self.painter.drawLine(self.origine_mvt.x(), self.origine_mvt.y()-5, self.origine_mvt.x(), self.origine_mvt.y()+5)
        self.painter.drawText(self.origine_mvt.x(), self.origine_mvt.y()+15, "O")
        
        ############################################################
        #Paint points
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
                    
 
            
            #self.painter.translate(-p.x()-self.origine.x()+ptreferentiel.x(), -p.y()-self.origine.y()+ptreferentiel.y())
            
                    
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
        self.painter.rotate(self.app.sens_X*self.app.sens_Y*(90))
        self.painter.translate(-self.origine_mvt.x(), -self.origine_mvt.y())
        ############################################################
        
        ############################################################
        #paint speed vectors if asked
        if self.speedToDraw!=[]:
            try: 
                
                p, vector_speed,i = self.speedToDraw[0],self.speedToDraw[1], self.speedToDraw[2]
                self.painter.setPen(QColor(self.couleurs[i-1]))
                print p, vector_speed
                #self.painter.translate(p.x()+self.origine.x()-ptreferentiel.x(), p.y()+self.origine.y()-ptreferentiel.y())
                #self.painter.drawLine(p,p+vector_speed)
                speed = sqrt(vector_speed.x()**2+vector_speed.y()**2)*float(self.app.echelle_image.mParPx())\
                        /(2*self.app.deltaT)*float(self.app.ui.checkBoxScale.currentText())
                print speed
                path = QPainterPath()
                path.moveTo(0, 0)
                path.lineTo(speed, 0)
                path.lineTo(QPointF(speed-10,0)+QPointF(0,10))
                path.lineTo(speed-8, 0)
                path.lineTo(QPointF(speed-10,0)+QPointF(0,-10))
                path.lineTo(speed, 0)
                
                #p1=QPoint(0,0)
                #p2=QPoint(speed,0)
                #p3=QPoint(speed-10,0)+QPoint(0,10)
                #p4=QPoint(speed-10,0)+QPoint(0,-10)
                
                angle = atan2(float(vector_speed.y()),float(vector_speed.x()))
                self.painter.translate(p)
                self.painter.rotate(degrees(angle))
                #self.painter.drawPolyline(p1,p2,p3,p4,p2)
                self.painter.drawPath(path)
                self.painter.fillPath(path, QColor(self.couleurs[i-1]))
                #restore painter
                self.painter.translate(-p)
                self.painter.rotate(-degrees(angle))
            except IndexError:
                pass #catch an undifined error TODO
            
        
        
        
        self.painter.end()
        
