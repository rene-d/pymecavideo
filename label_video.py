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
from PyQt4 import QtCore, QtGui
from glob import glob
from math import sqrt, acos, asin, pi, cos, sin, atan2
from vecteur import vecteur
from zoom import Zoom_Croix

class Label_Video(QtGui.QLabel):
    def __init__(self, parent, app):
        QtGui.QLabel.__init__(self,parent)
        self.setGeometry(QtCore.QRect(0,0,640,480))
        self.parent=parent
        self.liste_points = []
        self.app=app
        self.setCursor(QtCore.Qt.ArrowCursor)
        self.pos=self.pos_avant=vecteur(0,0)
        self.zoom_croix=Zoom_Croix(self,app)
        self.zoom_croix.hide()
        self.croixGeometry(self.pos)
        self.setMouseTracking(True)
    def reinit(self):
        self.zoom_croix=Zoom_Croix(self,self.app)
        self.croixGeometry(self.pos)
        self.met_a_jour_crop()
        self.setMouseTracking(True)
        self.zoom_croix.show()
    def croixGeometry(self, pos):
        """
        fixe dynamiquement la géométrie du widget
        """
        r=QtCore.QRect(pos.x()+5,pos.y()+5,100,100)
        self.zoom_croix.setGeometry(r)
        
    def mouseReleaseEvent(self, event):
        if self.app.lance_capture==True:
            self.liste_points.append(vecteur(event.x(), event.y()))
            #self.zoom_croix.hide()
            self.pos_avant=self.pos
            self.app.emit(QtCore.SIGNAL('clic_sur_video()'))
            #self.zoom_croix=Zoom_Croix(self,self.app)
            self.croixGeometry(self.pos)
            self.met_a_jour_crop()
    def enterEvent(self, event):
        if self.app.lance_capture==True:#ne se lance que si la capture est lancée
            self.zoom_croix.show()
            self.setCursor(QtCore.Qt.CrossCursor)
    def met_a_jour_crop(self):
        self.zoom_croix.fait_crop(self.pos_avant)
        self.croixGeometry(self.pos_avant)
    def leaveEvent(self, envent):
        if self.app.lance_capture==True:
            self.zoom_croix.hide()
    def mouseMoveEvent(self, event):
        if self.app.lance_capture==True:#ne se lance que si la capture est lancée
                self.pos=vecteur(event.x(), event.y())
                self.croixGeometry(self.pos)
                #print "mouse event label_video", self.pos
                self.zoom_croix.fait_crop(self.pos)
                self.zoom_croix.show()
                self.zoom_croix.update()
                self.zoom_croix.update()