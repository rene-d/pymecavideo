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
from PyQt6.QtGui import QKeySequence, QIcon, QPixmap, QImage, QPainter, QPen, QColor, QShortcut, QCursor
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QLayout, QFileDialog, QTableWidgetItem, QInputDialog, QLineEdit, QMessageBox, QTableWidgetSelectionRange

from vecteur import vecteur
from globdef import cible_icon

import os.path

class MonRect:
    def __init__(self, x1 = None, y1 = None, x2 = None, y2 = None):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        return

    def coords(self):
        return self.x1, self.y1, self.x2, self.y2

    def paint(self, painter):
        """
        méthode de dessin
        @param painter un QPainter actif
        """
        # trace un rectangle
        painter.drawRect(round(self.x1), round(self.y1),
                         round(self.x2 - self.x1),
                         round(self.y2 - self.y1))
        # puis trace les diagonales
        painter.drawLine(round(self.x1), round(self.y1),round(self.x2), round(self.y2))
        painter.drawLine(round(self.x1), round(self.y2),round(self.x2), round(self.y1))
        return
    

class SelRectWidget(QWidget):
    """
    Sert au retour visuel quand l'utilisateur doit sélectionner une
    zone rectangulaire pour le suivi automatique

    paramètres du constructeur:
    @param parent le widget parent, qui est un videoWidget
    @param pw un poitageWidget
    """
    def __init__(self, parent, pw):
        """make a rectangle near point to be tracked"""
        QWidget.__init__(self, parent)
        self.video = parent
        self.pw = pw
        self.echelle = self.video.image_w/pw.largeurFilm
        self.setGeometry(
            QRect(0, 0, self.video.image_w, self.video.image_h))
        self.setAutoFillBackground(False)
        cible_pix = QPixmap(cible_icon).scaledToHeight(32)
        cible_cursor = QCursor(cible_pix)
        self.setCursor(cible_cursor)
        self.setMouseTracking(True)
        self.rects = []
        self.dragging = False
        return

    def mousePressEvent(self, event):
        p = vecteur(qPoint = event.position())
        self.rects.append(MonRect(p.x, p.y, p.x, p.y))
        self.dragging = True
        self.update()
        return

    def mouseMoveEvent(self, event):
        p = vecteur(qPoint = event.position())
        self.pw.update_zoom.emit(p)

        if self.dragging:
            self.rects[-1].x2 = p.x
            self.rects[-1].y2 = p.y
        self.update()
        return

    def mouseReleaseEvent(self, event):
        self.dragging = False
        self.pw.motifs_auto.append(self.getMotif())
        self.pw.selection_motif_done.emit()
        self.update()
        return

    def getMotif(self):
        """
        récupère le motif qui servira à la reconnaissance automatique
        sur les images successives.
        @result un morceau d'image au format openCV, directement tiré du film
        """
        # on a un rectangle délimité par un pointage sur le videoWidget
        # qui a pu être redimensionné ; il faut en déduire un rectangle
        # dans l'image vidéo originale, d'où la division par self.echelle
        x1, y1, x2, y2 = self.rects[-1].coords()
        x = round(min(x1, x2) / self.echelle)
        y = round(min(y1, y2) / self.echelle)
        w = round(abs(x2-x1) / self.echelle)
        h = round(abs(y2-y1) / self.echelle)
        # on récupère la bonne image du film et on la découpe
        ok, image_opencv = self.pw.cvReader.getImage(
            self.pw.index, self.video.rotation, rgb=False)
        return image_opencv[y:y+h,x:x+w]

    def paintEvent(self, event):
        if self.rects:
            painter = QPainter()
            painter.begin(self)
            for rect in self.rects[:-1]:
                painter.setPen(QColor("red"))
                rect.paint(painter)
            painter.setPen(QColor("green"))
            self.rects[-1].paint(painter)
            painter.end()
        return
