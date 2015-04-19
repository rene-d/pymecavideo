# -*- coding: utf-8 -*-

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

import sys
import os
import thread
import time
import commands
from glob import glob
from math import sqrt, acos, asin, pi, cos, sin, atan2

from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import *
from PyQt4.QtGui import *

from vecteur import vecteur
from zoom import Zoom_Croix


class Label_Video(QtGui.QLabel):
    def __init__(self, parent, app):
        QtGui.QLabel.__init__(self, parent)
        self.parent = parent
        self.app = app
        self.setGeometry(QtCore.QRect(0, 0, self.app.largeur, self.app.hauteur))
        # self.setStyleSheet("background-color: grey");

        self.liste_points = []

        self.app.dbg.p(1, "In : Label_Video, __init__")
        self.cropX2 = None
        self.setCursor(QtCore.Qt.ArrowCursor)
        self.pos = self.pos_avant = vecteur(50, 50)
        self.zoom_croix = Zoom_Croix(self.app.ui.label_zoom, self.app)
        self.zoom_croix.hide()
        self.setMouseTracking(True)
        self.origine = vecteur(self.geometry().width() / 2, self.geometry().height() / 2)
        #####################TODO
        self.decal = vecteur(0, 0)  #if video is not 4:3, center video

        self.couleurs = ["red", "blue", "cyan", "magenta", "yellow", "gray", "green", "red", "blue", "cyan", "magenta",
                         "yellow", "gray", "green"]

    def reinit(self):
        try:
            del self.zoom_croix
        except:
            pass
        self.met_a_jour_crop()
        self.setMouseTracking(True)

    def storePoint(self, point):
        if self.app.lance_capture == True:
            self.liste_points.append(point)
            self.pos_avant = self.pos
            self.app.emit(SIGNAL('clic_sur_video()'))
            self.update()
            self.met_a_jour_crop()

    def mouseReleaseEvent(self, event):
        self.storePoint(vecteur(event.x(), event.y()))

    def enterEvent(self, event):
        if self.app.lance_capture == True and self.app.auto == False:  # ne se lance que si la capture est lancée
            self.setCursor(QtCore.Qt.CrossCursor)
        else:
            self.setCursor(QtCore.Qt.ArrowCursor)
    def maj(self):
        self.setGeometry(QtCore.QRect(0, 0, self.app.largeur, self.app.hauteur))

    def met_a_jour_crop(self):
        self.fait_crop(self.pos_avant)

    def leaveEvent(self, event):
        if self.app.lance_capture == True:
            self.cache_zoom()

    def mouseMoveEvent(self, event):
        if self.app.lance_capture == True and self.app.auto == False:  # ne se lance que si la capture est lancée
            self.zoom_croix.show()
            self.pos = vecteur(event.x(), event.y())
            self.fait_crop(self.pos)
            self.app.ui.label_zoom.setPixmap(self.cropX2)


    def cache_zoom(self):
        pass

    def paintEvent(self, event):

        if self.app.echelle_faite:
            self.fait_crop(self.pos)
            self.app.ui.label_zoom.setPixmap(self.cropX2)

        self.painter = QPainter()
        self.painter.begin(self)
        try:
            self.painter.drawPixmap(self.decal.x(), self.decal.y(), self.pixmap())
        except TypeError:  # pixmap is not declare yet
            pass

        ############################################################
        # paint the origin
        self.painter.setPen(Qt.green)
        self.painter.drawLine(self.origine.x() - 5, self.origine.y(), self.origine.x() + 5, self.origine.y())
        self.painter.drawLine(self.origine.x(), self.origine.y() - 5, self.origine.x(), self.origine.y() + 5)
        self.painter.drawText(self.origine.x(), self.origine.y() + 15, "O")



        ############################################################
        #draw points
        self.app.dbg.p(5, "In label_video, paintEvent, self.app.points :%s" % self.app.points)
        for points in self.app.points.values():  #all points clicked are stored here, but updated every "number of point to click" frames
            color = 0

            for point in points:
                if type(point) != type(""):
                    self.painter.setPen(QColor(self.couleurs[color]))
                    self.painter.setFont(QFont("", 10))
                    self.painter.translate(point.x(), point.y())
                    self.painter.drawLine(-2, 0, 2, 0)
                    self.painter.drawLine(0, -2, 0, 2)
                    self.painter.translate(-10, +10)
                    self.painter.drawText(0, 0, str(color + 1))

                    self.painter.translate(-point.x() + 10, -point.y() - 10)

                    color += 1
        color = 0
        if self.liste_points != []:

            for point in self.liste_points:  #points clicked in a "number of point to click" sequence.

                self.painter.setPen(QColor(self.couleurs[color]))
                self.painter.setFont(QFont("", 10))
                self.painter.translate(point.x(), point.y())
                self.painter.drawLine(-2, 0, 2, 0)
                self.painter.drawLine(0, -2, 0, 2)
                self.painter.translate(-10, +10)
                self.painter.drawText(0, 0, str(color + 1))

                self.painter.translate(-point.x() + 10, -point.y() - 10)
                color += 1
                ############################################################

        ############################################################
        #paint repere
        self.painter.setPen(Qt.green)
        self.painter.translate(0, 0)
        self.painter.translate(self.origine.x(), self.origine.y())
        p1 = QPoint(self.app.sens_X * (-40), 0)
        p2 = QPoint(self.app.sens_X * (40), 0)
        p3 = QPoint(self.app.sens_X * (36), 2)
        p4 = QPoint(self.app.sens_X * (36), -2)
        self.painter.scale(1, 1)
        self.painter.drawPolyline(p1, p2, p3, p4, p2)
        self.painter.rotate(self.app.sens_X * self.app.sens_Y * (-90))
        self.painter.drawPolyline(p1, p2, p3, p4, p2)
        ############################################################


        self.painter.end()


    def fait_crop(self, p):
        rect = QRect(p.x() - 25, p.y() - 25, 50, 50)
        crop = self.app.imageAffichee.copy(rect)
        self.cropX2 = QPixmap.fromImage(crop.scaled(100, 100, Qt.KeepAspectRatio))
