#-*- coding: utf-8 -*-

"""
    videotraj, a module for pymecavideo:
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

import sys, os, thread, time, commands
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from glob import glob
from math import sqrt, acos, asin, pi, cos, sin, atan2
from vecteur import vecteur
from zoom import Zoom_Croix

class Label_Video(QtGui.QLabel):
    def __init__(self, parent, app):
        QtGui.QLabel.__init__(self,parent)
        self.setGeometry(QtCore.QRect(0,0,640,480))
        #self.setStyleSheet("background-color: grey");
        self.parent=parent
        self.liste_points = []
        self.app=app
        self.cropX2=None
        self.setCursor(QtCore.Qt.ArrowCursor)
        self.pos=self.pos_avant=vecteur(0,0)
        self.zoom_croix = Zoom_Croix(self.app.ui.label_zoom)
        self.zoom_croix.hide()
        self.setMouseTracking(True)
        self.couleurs=["red", "blue", "cyan", "magenta", "yellow", "gray", "green"]
    def reinit(self):
        try :
            del self.zoom_croix
        except :
            pass
        self.met_a_jour_crop()
        self.setMouseTracking(True)
        
    def mouseReleaseEvent(self, event):
        
        if self.app.lance_capture==True and self.app.auto==False:
            self.liste_points.append(vecteur(event.x(), event.y()))
            self.pos_avant=self.pos
            self.app.emit(QtCore.SIGNAL('clic_sur_video()'))

            self.met_a_jour_crop()
    def enterEvent(self, event):
        if self.app.lance_capture==True and self.app.auto==False:#ne se lance que si la capture est lancée
            self.setCursor(QtCore.Qt.CrossCursor)
        else :
            self.setCursor(QtCore.Qt.ArrowCursor)
    def met_a_jour_crop(self):
        self.fait_crop(self.pos_avant)
    def leaveEvent(self, envent):
        if self.app.lance_capture==True:
            self.cache_zoom()
    def mouseMoveEvent(self, event):
        if self.app.lance_capture==True and self.app.auto==False:#ne se lance que si la capture est lancée
                self.zoom_croix.show()
                self.pos=vecteur(event.x(), event.y())
                self.fait_crop(self.pos)
                self.app.ui.label_zoom.setPixmap(self.cropX2)
                
    def cache_zoom(self):
        pass

    def paintEvent(self,event):
        
        self.painter = QPainter()
        self.painter.begin(self)
        self.painter.drawPixmap(0,0,self.pixmap())
        for points in self.app.points.values() :      
            color=0
            for point in points:
                if type(point)!= type(""): 
                    self.painter.setPen(QColor(self.couleurs[color]))
                    self.painter.setFont(QFont("", 10))
                    self.painter.translate(point.x(), point.y())
                    self.painter.drawLine(-2,0,2,0)
                    self.painter.drawLine(0,-2,0,2)
                    self.painter.translate(-10, +10)
                    self.painter.drawText(0,0,str(color+1))
                    
                    self.painter.translate(-point.x()+10, -point.y()-10)
                    
                    color+=1
                #except AttributeError:
                    #print type(point)
                    #pass #needed as first thing in "points" is its number.
                
        self.painter.end()
        
        
    def fait_crop(self, p):
        rect = QRect(p.x()-25,p.y()-25,50,50)
        crop = self.app.image_640_480.copy(rect)
        self.cropX2=QPixmap.fromImage(crop.scaled(100,100,Qt.KeepAspectRatio))
