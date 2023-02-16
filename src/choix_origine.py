# -*- coding: utf-8 -*-
"""
    choix_origine, a module for pymecavideo:
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
from PyQt6.QtCore import QThread, pyqtSignal, QLocale, QTranslator, Qt, QSize, QTimer, QObject, QRect, QPoint, QPointF
from PyQt6.QtGui import QKeySequence, QIcon, QPixmap, QImage, QPainter, QPen, QColor, QShortcut
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QLayout, QFileDialog, QTableWidgetItem, QInputDialog, QLineEdit, QMessageBox, QTableWidgetSelectionRange

from vecteur import vecteur


class ChoixOrigineWidget(QWidget):
    """
    Un widget pour choisir une nouvelle origine ; il est posé sur le
    widget vidéo, et durant sa vie, il permet d'avoir un retour visuel
    pendant qu'on bouge la souris vers la nouvelle origine.
    """
    
    def __init__(self, parent, app):
        QWidget.__init__(self, parent)
        self.parent = parent
        self.app = app
        self.setGeometry(
            QRect(0, 0, self.parent.width(), self.parent.height()))
        self.setAutoFillBackground(False)

        self.setCursor(Qt.CursorShape.CrossCursor)
        self.cropX2 = None
        self.setMouseTracking(True)

    def mouseMoveEvent(self, event):
        p = vecteur(qPoint = event.position())
        self.app.update_zoom.emit(p)
        return

    def mouseReleaseEvent(self, event):
        p = vecteur(qPoint = event.position())
        self.app.video.origine = p
        self.app.update_zoom.emit(p)

        self.app.egalise_origine()
        self.close()
