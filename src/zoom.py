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
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from math import sqrt, acos, asin, pi, cos, sin, atan2
from vecteur import vecteur

class Zoom_Croix(QWidget):
    def __init__(self, parent,app):

        QWidget.__init__(self, parent)
        self.parent = parent
        self.app = app
        print app, parent
        
        self.setEnabled(True)
        self.setGeometry(QRect(0, 0, 100, 100))
        self.setAutoFillBackground(False)
        
    def paintEvent(self, event):
                painter = QPainter()
                painter.begin(self)
                painter.setPen(Qt.red)
                painter.drawLine(50, 0, 50, 100)
                painter.drawLine(0, 50, 100, 50)
