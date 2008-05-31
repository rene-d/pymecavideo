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
from glob import glob
from math import sqrt, acos, asin, pi, cos, sin, atan2
from vecteur import vecteur

class Zoom(QLabel):
    def __init__(self, parent):
        QLabel.__init__(self, parent)
        self.parent = parent
    def fait_crop(self, x, y):
        rect = QRect(x-25,y-25,50,50)
        crop = self.parent.app.image_640_480.copy(rect)
	cropX2=crop.scaled(100,100,Qt.KeepAspectRatio, Qt.SmoothTransformation)
        return cropX2

class Zoom_Croix(QLabel):
    def __init__(self, parent):
        QLabel.__init__(self, parent)
        self.parent = parent
    def fait_crop(self, x, y):
        rect = (x-25,y-25,50,50)
        crop = self.parent.app.image.copy(rect)
        cropX2=crop.scaled(100,100,Qt.KeepAspectRatio)
        return cropX2
    
    def paintEvent(self, event):
        if self.parent.app.lance_capture==True:
            painter = QPainter()
            painter.begin(self)
           
            painter.setPen(Qt.white)
            painter.drawLine(50, 0, 50, 100)
            painter.drawLine(0, 50, 100, 50)
