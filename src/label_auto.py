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

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from vecteur import vecteur


class Label_Auto(QLabel):
    def __init__(self, parent, app):
        """make a rectangle near point to be tracked"""
        QLabel.__init__(self, parent)
        self.parent = parent
        self.app = app
        self.setGeometry(QRect(0, 0, self.app.largeur, self.app.hauteur))
        self.setAutoFillBackground(False)

        self.setCursor(Qt.CrossCursor)
        self.setMouseTracking(True)

    def mousePressEvent(self, event):
        self.setMouseTracking(False)
        self.x_1 = event.x()
        self.x_2 = event.x()
        self.y_1 = event.y()
        self.y_2 = event.y()

    def mouseMoveEvent(self, event):
        x = event.x()
        y = event.y()

        if not self.hasMouseTracking():
            if x > self.x_1:
                self.x_2 = x
            elif x < self.x_1:
                self.x_1 = x
            if y > self.y_1:
                self.y_2 = y
            elif y < self.y_1:
                self.y_1 = y
        self.pos = vecteur(x, y)
        self.parent.pos = self.pos
        self.app.label_video.zoom_croix.show()

        self.app.label_video.fait_crop(self.pos)
        self.app.ui.label_zoom.setPixmap(self.app.label_video.cropX2)
        self.update()

    def mouseReleaseEvent(self, event):
        self.app.zoom = True
        self.app.motif.append(self.getMotif())
        self.app.emit(SIGNAL('selection_motif_done()'))


    def getMotif(self):
        """
        récupère le motif qui servira à la reconnaissance automatique
        sur les images successives.
        @result une QImage représentant le motif.
        """
        rectangle = QRect(self.x_1, self.y_1, self.x_2 - self.x_1, self.y_2 - self.y_1)
        return self.app.imageAffichee.copy(rectangle)


    def paintEvent(self, event):
        if not self.hasMouseTracking():
            painter = QPainter()
            painter.begin(self)
            painter.setPen(Qt.green)
            painter.drawRect(self.x_1, self.y_1, self.x_2 - self.x_1, self.y_2 - self.y_1)
            painter.end()



