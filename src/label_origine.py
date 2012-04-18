# -*- coding: utf-8 -*-
"""
    Label_Origine, a module for pymecavideo:
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
from zoom import Zoom_Croix


class Label_Origine(QLabel):
    def __init__(self, parent,app):
        QLabel.__init__(self, parent)
        self.parent = parent
        self.setGeometry(QRect(0,0,640,480))
        self.setAutoFillBackground(False)
        self.app = app
        self.setCursor(Qt.CrossCursor)
        self.cropX2=None
        self.zoom_croix = Zoom_Croix(self.app.ui.label_zoom)
        self.zoom_croix.hide()
        self.setMouseTracking(True)
        
    def mouseMoveEvent(self, event):
        self.zoom_croix.show()
        self.pos=vecteur(event.x(), event.y())
        self.fait_crop(self.pos)
        self.app.ui.label_zoom.setPixmap(self.cropX2)
        
    def fait_crop(self, p):
        rect = QRect(p.x()-25,p.y()-25,50,50)
        crop = self.app.image_640_480.copy(rect)
        self.cropX2=QPixmap.fromImage(crop.scaled(100,100,Qt.KeepAspectRatio))


    def mouseReleaseEvent(self, event):
        self.app.origine = vecteur(event.x() + 1, event.y() + 1)
        
        #try :
            #self.app.origine_trace.hide()
            #del self.app.origine_trace
        #except :
            #pass
        self.zoom_croix.hide()
        self.app.ui.label_zoom.setPixmap(QPixmap(None))
        del self.zoom_croix
        self.app.emit(SIGNAL('change_axe_origine()'))

        self.close()