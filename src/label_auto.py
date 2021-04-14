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

from PyQt5.QtCore import QThread, pyqtSignal, QLocale, QTranslator, Qt, QSize, QTimer, QObject, QRect, QPoint, QPointF
from PyQt5.QtGui import QKeySequence, QIcon, QPixmap, QImage, QPainter, QCursor, QPen, QColor
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QWidget, QShortcut, QDesktopWidget, QLayout, QFileDialog, QTableWidgetItem, QInputDialog, QLineEdit, QMessageBox, QTableWidgetSelectionRange

from vecteur import vecteur
import os.path


class Label_Auto(QLabel):
    def __init__(self, parent, app):
        """make a rectangle near point to be tracked"""
        QLabel.__init__(self, parent)
        self.parent = parent
        self.app = app
        self.setGeometry(
            QRect(0, 0, self.app.label_video.width(), self.app.label_video.height()))
        self.setAutoFillBackground(False)

        # prend un beau gros curseur rouge inmanquable
        self.cible_icon = os.path.join(
            self.app._dir("icones"), "curseur_cible.svg")
        pix = QPixmap(self.cible_icon).scaledToHeight(32, 32)
        self.cursor = QCursor(pix)
        self.setCursor(self.cursor)

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

        if not self.hasMouseTracking():  # lancé lors de la sélection.
            self.x_2 = x
            self.y_2 = y
        self.pos_zoom = vecteur(x, y)
        self.parent.pos_zoom = self.pos_zoom
        self.app.label_video.zoom_croix.show()

        self.app.label_video.fait_crop(self.pos_zoom)
        self.app.ui.label_zoom.setPixmap(self.app.label_video.cropX2)
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
