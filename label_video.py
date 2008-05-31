#-*- coding: utf-8 -*-

"""
    videotraj, a module for pymecavideo:
      a program to track moving points in a video frameset
      
    Copyright (C) 2007 Jean-Baptiste Butet <ashashiwa@gmail.com>

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 2 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import sys, os, thread, time, commands
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from glob import glob
from math import sqrt, acos, asin, pi, cos, sin, atan2
from vecteur import vecteur
from zoom import Zoom, Zoom_Croix

class Label_Video(QLabel):
    def __init__(self, parent, app):
        QLabel.__init__(self,parent)
        self.setGeometry(QRect(0,0,640,480))
        self.parent=parent
        self.liste_points = []
        self.app=app
        self.setCursor(Qt.ArrowCursor)
        self.x1=self.y1 = 0
        self.zoom=Zoom(self)
        self.zoom_croix=Zoom_Croix(self)
        self.zoom.setGeometry(QRect(self.x1,self.y1,100,100))
        self.zoom_croix.setGeometry(QRect(self.x1,self.y1,100,100))
        #self.zoom.setPixmap(.QPixmap("croix.png"))

        
    def mouseReleaseEvent(self, event):
        self.liste_points.append(vecteur(event.x(), event.y()))
        self.zoom.hide()
        self.zoom_croix.hide()
        self.app.emit(SIGNAL('clic_sur_video()'))

    def mouseMoveEvent(self, event):
        if self.app.lance_capture==True:#ne se lance que si la capture est lancée
            self.x1 = event.x() +1
            self.y1 = event.y() +1
	    
            self.zoom.setGeometry(QRect(self.x1+5,self.y1+5,100,100))
            self.zoom_croix.setGeometry(QRect(self.x1+5,self.y1+5,100,100))
            cropX2=self.zoom.fait_crop(self.x1, self.y1)
            #self.zoom.setPixmap(.QPixmap.fromImage(ImageQt.ImageQt(image_crop)))
            self.zoom.setPixmap(QPixmap.fromImage(cropX2))
            self.zoom.show()
            self.zoom_croix.show()
            self.zoom.update()
            self.zoom_croix.update()