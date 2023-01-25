# -*- coding: utf-8 -*-
"""
    echelle, a module for pymecavideo:
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

from math import sqrt
import os

from PyQt6.QtCore import QThread, pyqtSignal, QLocale, QTranslator, Qt, QSize, QTimer, QObject, QRect
from PyQt6.QtGui import QKeySequence, QIcon, QPixmap, QImage, QPainter, QCursor, QShortcut
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QLayout, QFileDialog, QTableWidgetItem, QInputDialog, QLineEdit, QMessageBox, QTableWidgetSelectionRange

from vecteur import vecteur
from globdef import beauGrosCurseur

class echelle(QObject):
    def __init__(self, p1=vecteur(0, 0), p2=vecteur(0, 0)):
        self.p1, self.p2 = p1, p2
        self.longueur_reelle_etalon = 1
        # si les deux points sont distincts, l'échelle est faite
        return

    def __bool__(self):
        """
        @return vrai si l'échelle a été faite
        """
        return self.p1 != self.p2
    
    def __str__(self):
        return "echelle(%s,%s,%s m)" % (self.p1, self.p2, self.longueur_reelle_etalon)

    def longueur_pixel_etalon(self):
        return (self.p1 - self.p2).norme

    def isUndef(self):
        """
        Vrai si l'échelle n'est pas définie, c'est à dire si
        p1 et p2 sont confondus.
        """
        return not self

    def mParPx(self):
        """renvoie le nombre de mètre par pixel"""
        if not self.isUndef():
            return self.longueur_reelle_etalon / self.longueur_pixel_etalon()
        else:
            return 1

    def pxParM(self):
        """renvoie le nombre de pixel par mètre"""
        if not self.isUndef():
            return self.longueur_pixel_etalon() / self.longueur_reelle_etalon
        else:
            return 1

    def applique_echelle(self, pos_echelle):
        """
        les positions pos sont en pixels, ça renvoie une liste
        de positions (vecteurs) en mètre. L'origine est en (0, self.app.hauteur)
        """
        return [(vecteur(0, self.app.hauteur) - p) * self.mParPx()
                for p in pos_echelle]

    def etalonneReel(self, l):
        """
        Définit la longueur en mètre de l'étalon
        @param l longueur en mètre
        """
        self.longueur_reelle_etalon = float(l)


class EchelleWidget(QWidget):
    """
    Widget qui permet de définir l'échelles

    Paramètres du constructeur :
    @param parent le widget parent
    @param app pointeur vers l'application

    Propiétés
    @prop self.p1 vecteur
    @prop self.p2 vecteur
    ...
    """
    def __init__(self, parent, app):
        QWidget.__init__(self, parent)
        self.video = parent
        self.app = app
        self.image=None
        self.setGeometry(
            QRect(0, 0, self.video.width(), self.video.height()))
        self.largeur = self.video.width()
        self.hauteur = self.video.height()
        self.setAutoFillBackground(False)
        self.p1 = vecteur()
        self.p2 = vecteur()
        self.pos_echelle = vecteur()
        beauGrosCurseur(self)
        self.cropX2 = None
        self.setMouseTracking(True)
        self.pressed = False
        try:
            # origine definition is optionnal but hide scale if defined first
            self.app.origine_trace.lower()
        except AttributeError:
            pass
        try:
            self.app.echelle_trace.hide()
            del self.app.echelle_trace
        except AttributeError:
            pass
        return

    def mousePressEvent(self, event):
        if event.button() != 1:
            self.p1 = vecteur(-1, -1)
            self.close()
        self.p1 = vecteur(event.x(), event.y())
        self.pressed = True

    def paintEvent(self, event):
        painter = QPainter()
        painter.begin(self)

        painter.setPen(Qt.red)
        if self.p1.x > 0:
            painter.drawLine(round(self.p1.x), round(self.p1.y),
                             round(self.p2.x), round(self.p2.y))
        painter.end()

    def mouseMoveEvent(self, event):
        if (event.x() > 0 and event.x() < self.largeur) and (event.y() > 0 and event.y() < self.hauteur):
            self.video.updateZoom(vecteur(event.x(), event.y()))

        if self.pressed:
            self.p2 = vecteur(event.x(), event.y())
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == 1 and self.p1.x >= 0:
            self.p2 = vecteur(event.x(), event.y())
        self.video.updateZoom()
        self.video.index_du_point = 0

        self.video.echelle_image.p1 = self.p1.copy()
        self.video.echelle_image.p2 = self.p2.copy()

        epxParM = self.video.echelle_image.pxParM()
        self.video.affiche_echelle()
        # self.app.affiche_nb_points(True)
        self.app.affiche_barre_statut(self.app.tr(
            u"Choisir le nombre de points puis « Démarrer l'acquisition » "))
        self.video.mets_en_orange_echelle()

        self.video.feedbackEchelle(self.p1, self.p2)
        self.app.fixeLesDimensions()
        self.video.egalise_origine()
        if self.video.data:  # si on a déjà pointé une position au moins
            self.app.affiche_barre_statut(self.app.tr(
                "Vous pouvez continuer votre acquisition"))
            self.app.refait_echelle()

        self.close()


class Echelle_TraceWidget(QWidget):
    def __init__(self, parent, p1, p2):
        QWidget.__init__(self, parent)
        self.video = parent
        self.image = None
        self.setGeometry(
            QRect(0, 0, self.video.width(), self.video.height()))
        self.setAutoFillBackground(False)
        self.p1 = p1
        self.p2 = p2
        self.setMouseTracking(True)

    def mouseMoveEvent(self, event):
        event.ignore()

    def mouseReleaseEvent(self, event):
        event.ignore()

    def maj(self):
        self.setGeometry(
            QRect(0, 0, self.video.width(), self.video.height()))

    def paintEvent(self, event):
        painter = QPainter()
        painter.begin(self)
        try:
            painter.setPen(Qt.green)
            painter.drawLine(round(self.p1.x), round(self.p1.y),
                             round(self.p2.x), round(self.p2.y))
        except AttributeError:
            pass  # arrive au premier lancement sans vidéos
        painter.end()
