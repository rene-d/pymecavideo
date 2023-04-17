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
from PyQt6.QtGui import QKeySequence, QIcon, QPixmap, QImage, QPainter, QShortcut, QColor, QCursor
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QLayout, QFileDialog, QTableWidgetItem, QInputDialog, QLineEdit, QMessageBox, QTableWidgetSelectionRange

from vecteur import vecteur
from globdef import cible_icon

class echelle(QObject):
    def __init__(self, p1=vecteur(0, 0), p2=vecteur(0, 0)):
        self.p1, self.p2 = p1, p2
        self.longueur_reelle_etalon = 1
        # si les deux points sont distincts, l'échelle est faite
        return

    def __str__(self):
        """
        donne une vision partielle de l'instance courante
        """
        return f"echelle(p1 = {self.p1}, p2 = {self.p2}, longueur_reelle_etalon = {self.longueur_reelle_etalon})"
    
    def __bool__(self):
        """
        @return vrai si l'échelle a été faite
        """
        return self.p1 != self.p2 and (self.p1 - self.p2).norme > 1
    
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

    def etalonneReel(self, l):
        """
        Définit la longueur en mètre de l'étalon
        @param l longueur en mètre
        """
        self.longueur_reelle_etalon = float(l)
        return


class EchelleWidget(QWidget):
    """
    Widget qui permet de définir l'échelles

    Paramètres du constructeur :
    @param parent le widget video
    @param pw  widget principal de l'onglet pointage
    @param app pointeur vers l'application

    Propiétés
    @prop self.p1 vecteur
    @prop self.p2 vecteur
    ...
    """
    def __init__(self, parent, pw):
        QWidget.__init__(self, parent)
        if hasattr(pw, "app"):
            self.app = pw.app     # la fenêtre principale
        self.video = parent       # l'afficheur de vidéo
        self.pw = pw              # le widget de l'onglet de pointage
        self.image=None
        if self.video:
            self.setGeometry(
                QRect(0, 0, self.video.image_w, self.video.image_h))
            self.largeur = self.video.image_w
            self.hauteur = self.video.image_h
        self.setAutoFillBackground(False)
        self.p1 = vecteur()
        self.p2 = vecteur()
        self.pos_echelle = vecteur()
        cible_pix = QPixmap(cible_icon).scaledToHeight(32)
        cible_cursor = QCursor(cible_pix)
        self.setCursor(cible_cursor)
        self.cropX2 = None
        self.setMouseTracking(True)
        self.pressed = False
        return

    def paintEvent(self, event):
        if self.p1.x <= 0 or self.p2.x <= 0: return
        painter = QPainter()
        painter.begin(self)

        painter.setPen(QColor("red"))
        painter.drawLine(round(self.p1.x), round(self.p1.y),
                         round(self.p2.x), round(self.p2.y))
        painter.end()
        return

    def mousePressEvent(self, event):
        if event.button() != Qt.MouseButton.LeftButton:
            self.p1 = vecteur(-1, -1)
            self.close()
        self.p1 = vecteur(qPoint = event.position())
        self.pressed = True
        return

    def mouseMoveEvent(self, event):
        p = vecteur(qPoint = event.position())
        if self.pw.etat in ( 'C' , 'D') :
            self.pw.remet_zoom.emit()
            self.pw.update_zoom.emit(p)
        if self.pressed:
            self.p2 = p
            self.update()
        return

    def mouseReleaseEvent(self, event):
        p = vecteur(qPoint = event.position())
        self.pressed = False
        if event.button() == Qt.MouseButton.LeftButton and self.p1.x >= 0:
            self.p2 = p
            self.pw.echelle_image.p1 = self.p1.copy()
            self.pw.echelle_image.p2 = self.p2.copy()

            self.pw.affiche_echelle()
            self.app.affiche_statut.emit(self.tr("Échelle définie"))
            self.pw.echelle_modif.emit(self.tr("Refaire l'échelle"), "background-color:orange;")
            self.pw.index_du_point = 0

            self.pw.feedbackEchelle()
            self.app.stopRedimensionnement.emit()
            if self.pw.data:  # si on a déjà pointé une position au moins
                self.app.affiche_statut.emit(self.tr(
                    "Vous pouvez continuer votre acquisition"))
                self.app.coord.recalculLesCoordonnees()

        self.close()
        self.pw.apres_echelle.emit()
        self.pw.disable_zoom.emit()
        return

class Echelle_TraceWidget(QWidget):
    """
    Un widget transparent qui sert seulement à tracer l'échelle

    Paramètres du constructeur :
    @param parent un videoWidget
    @param p1 origine de l'étalon
    @param p2 extrémité de l'étalon
    """
    def __init__(self, parent, p1, p2):
        QWidget.__init__(self, parent)
        self.video = parent
        self.image = None
        self.setGeometry(
            QRect(0, 0, self.video.image_w, self.video.image_h))
        self.setAutoFillBackground(False)
        self.p1 = p1
        self.p2 = p2
        self.setMouseTracking(True)
        return

    def maj(self):
        self.setGeometry(
            QRect(0, 0, self.video.image_w, self.video.image_h))
        return

    def paintEvent(self, event):
        if self.p1.x <= 0 or self.p2.x <= 0: return

        painter = QPainter()
        painter.begin(self)
        painter.setPen(QColor("green"))
        painter.drawLine(round(self.p1.x), round(self.p1.y),
                         round(self.p2.x), round(self.p2.y))
        painter.end()
        return
