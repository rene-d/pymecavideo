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

    Paramètres du constructeur:
    @param parent un videoWidget
    @param pw le widget principal de l'onglet de pointage
    """
    
    def __init__(self, parent, pw):
        QWidget.__init__(self, parent)
        self.pw = pw
        self.setAutoFillBackground(False)
        self.setGeometry(QRect(0, 0, parent.image_w, parent.image_h))
        self.setCursor(Qt.CursorShape.CrossCursor)
        self.cropX2 = None
        self.setMouseTracking(True)

    def mouseMoveEvent(self, event):
        self.pw.update_zoom.emit(vecteur(qPoint = event.position()))
        return

    def mouseReleaseEvent(self, event):
        p = vecteur(qPoint = event.position())
        self.pw.origine = p
        self.pw.update_zoom.emit(p)
        self.pw.app.egalise_origine()
        self.close()
        return
