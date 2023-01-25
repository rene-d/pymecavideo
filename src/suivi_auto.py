# -*- coding: utf-8 -*-

"""
    suivi_auto, a module for pymecavideo:
      a program to track moving points in a video frameset
      
    Copyright (C) 2007 Jean-Baptiste Butet <ashashiwa@gmail.com>
    Copyright (C) 2023 Georges Khaznadar <georgesk@debian.org>

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

from PyQt6.QtCore import QThread, pyqtSignal, QLocale, QTranslator, Qt, QSize, QTimer, QObject, QRect, QPoint, QPointF
from PyQt6.QtGui import QKeySequence, QIcon, QPixmap, QImage, QPainter, QCursor, QPen, QColor, QShortcut
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QLayout, QFileDialog, QTableWidgetItem, QInputDialog, QLineEdit, QMessageBox, QTableWidgetSelectionRange

from vecteur import vecteur
from globdef import beauGrosCurseur
import os.path


class SelRectWidget(QWidget):
    """
    Sert au retour visuel quand l'utilisateur doit sélectionner une
    zone rectangulaire pour le suivi automatique

    paramètres du constructeur:
    @param parent le widget parent, qui est un VideoWidget
    """
    def __init__(self, parent):
        """make a rectangle near point to be tracked"""
        QWidget.__init__(self, parent)
        self.video = parent
        self.echelle = parent.image_w/parent.largeurFilm
        self.setGeometry(
            QRect(0, 0, self.video.image_w, self.video.image_h))
        self.setAutoFillBackground(False)
        beauGrosCurseur(self)
        return

    def finish(self, delete=False):
        """
        Cache le rectangle de sélection
        @param delete s'il est vrai, l'objet se détruit lui-même
        """
        self.hide()
        self.close()
        if delete:
            del self
        return
        
    def mousePressEvent(self, event):
        self.setMouseTracking(False)
        self.x_1 = event.x()
        self.x_2 = event.x()
        self.y_1 = event.y()
        self.y_2 = event.y()

    def mouseMoveEvent(self, event):
        x = event.x()
        y = event.y()

        if not self.hasMouseTracking():  # lancé lors de la sélection.
            self.x_2 = x
            self.y_2 = y
        self.video.updateZoom(vecteur(x, y))
        self.update()

    def mouseReleaseEvent(self, event):
        self.video.motifs_auto.append(self.getMotif())
        self.video.selection_motif_done.emit()

    def getMotif(self):
        """
        récupère le motif qui servira à la reconnaissance automatique
        sur les images successives.
        @result un morceau d'image au format openCV, directement tiré du film
        """
        # on a un rectangle délimité par un pointage sur le videoWidget
        # qui a pu être redimensionné ; il faut en déduire un rectangle
        # dans l'image vidéo originale, d'où la division par self.echelle
        x = round(min(self.x_1, self.x_2) / self.echelle)
        y = round(min(self.y_1, self.y_2) / self.echelle)
        w = round(abs(self.x_2 - self.x_1) / self.echelle)
        h = round(abs(self.y_2 - self.y_1) / self.echelle)
        # on récupère la bonne image du film et on la découpe
        ok, image_opencv = self.video.cvReader.getImage(
            self.video.index, self.video.rotation, rgb=False)
        return image_opencv[y:y+h,x:x+w]

    def paintEvent(self, event):
        if not self.hasMouseTracking():
            painter = QPainter()
            painter.begin(self)
            painter.setPen(Qt.green)
            painter.drawRect(self.x_1, self.y_1, self.x_2 -
                             self.x_1, self.y_2 - self.y_1)
            painter.end()
