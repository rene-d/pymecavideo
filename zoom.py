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
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from math import sqrt, acos, asin, pi, cos, sin, atan2
from vecteur import vecteur

class Zoom_Croix(QWidget):
    def __init__(self, parent):
        QWidget.__init__(self, parent)
        self.parent = parent
        self.setEnabled(True)
        self.setGeometry(QRect(0, 0, 100, 100))
        self.setAutoFillBackground(False)
        
    #def mouseMoveEvent(self, event):
        #event.ignore()
    #def mouseReleaseEvent(self, event):
        #event.ignore()
    #def fait_crop(self, p):
        #rect = QRect(p.x()-25,p.y()-25,50,50)
        #crop = self.app.image_640_480.copy(rect)
        #self.cropX2=QPixmap.fromImage(crop.scaled(100,100,Qt.KeepAspectRatio))
    #def hideEvent(self, event):
        #self.setGeometry(-1000,-1000,100,100)
        #self.update()
        #le bug vient du fait qu'il est caché..;mais pourquoi
        
    def paintEvent(self, event):
        #if self.app.lance_capture==True:
            #if self.cropX2 != None :
                painter = QPainter()
                painter.begin(self)
                painter.setPen(Qt.red)
                painter.drawLine(50, 0, 50, 100)
                painter.drawLine(0, 50, 100, 50)
