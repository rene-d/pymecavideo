# -*- coding: utf-8 -*-

"""
    suivi_auto, a module for pymecavideo:
      a program to track moving points in a video frameset
      
    Copyright (C) 2007 Jean-Baptiste Butet <ashashiwa@gmail.com>
    Copyright (C) 2022 Georges Khaznadar <georgesk@debian.org>

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

from PyQt5.QtCore import QThread, pyqtSignal, QLocale, QTranslator, Qt, QSize, QTimer, QObject, QRect, QPoint, QPointF
from PyQt5.QtGui import QKeySequence, QIcon, QPixmap, QImage, QPainter, QCursor, QPen, QColor
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QShortcut, QDesktopWidget, QLayout, QFileDialog, QTableWidgetItem, QInputDialog, QLineEdit, QMessageBox, QTableWidgetSelectionRange

from vecteur import vecteur
from globdef import beauGrosCurseur
import os.path


class SelRectWidget(QWidget):
    """
    Sert au retour visuel quand l'utilisateur doit sélectionner une
    zone rectangulaire pour le suivi automatique
    """
    def __init__(self, parent, app):
        """make a rectangle near point to be tracked"""
        QWidget.__init__(self, parent)
        self.parent = parent
        self.app = app
        self.setGeometry(
            QRect(0, 0, self.app.video.width(), self.app.video.height()))
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
        self.app.video.updateZoom(vecteur(x, y))
        self.update()

    def mouseReleaseEvent(self, event):
        self.app.zoom = True
        self.app.motif.append(self.getMotif())
        self.app.selection_motif_done.emit()

    def getMotif(self):
        """
        récupère le motif qui servira à la reconnaissance automatique
        sur les images successives.
        @result une QImage représentant le motif.
        """
        x_depart = self.x_1 if self.x_1 < self.x_2 else self.x_2
        y_depart = self.y_1 if self.y_1 < self.y_2 else self.y_2
        longueur = abs(self.x_2 - self.x_1)
        hauteur = abs(self.y_2 - self.y_1)

        rectangle = QRect(x_depart, y_depart, longueur, hauteur)
        return self.app.imageAffichee.copy(rectangle)

    def paintEvent(self, event):
        if not self.hasMouseTracking():
            painter = QPainter()
            painter.begin(self)
            painter.setPen(Qt.green)
            painter.drawRect(self.x_1, self.y_1, self.x_2 -
                             self.x_1, self.y_2 - self.y_1)
            painter.end()
