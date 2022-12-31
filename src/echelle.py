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

from PyQt5.QtCore import QThread, pyqtSignal, QLocale, QTranslator, Qt, QSize, QTimer, QObject, QRect
from PyQt5.QtGui import QKeySequence, QIcon, QPixmap, QImage, QPainter, QCursor
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QShortcut, QDesktopWidget, QLayout, QFileDialog, QTableWidgetItem, QInputDialog, QLineEdit, QMessageBox, QTableWidgetSelectionRange

from vecteur import vecteur
import os


class echelle(QObject):
    def __init__(self, p1=vecteur(0, 0), p2=vecteur(0, 0)):
        self.p1, self.p2 = p1, p2
        self.longueur_reelle_etalon = 1
        self.estdefinie = False

    def __str__(self):
        return "echelle(%s,%s,%s m)" % (self.p1, self.p2, self.longueur_reelle_etalon)

    def longueur_pixel_etalon(self):
        return (self.p1 - self.p2).norme

    def isUndef(self):
        """
        Vrai si l'échelle n'est pas définie, c'est à dire si
        p1 et p2 sont confondus.
        """
        return (self.p1 - self.p2).norme == 0

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
    @param parent le widegt parent
    @param app pointeur vers l'application

    Propiétés
    @prop self.p1 vecteur
    @prop self.p2 vecteur
    ...
    """
    def __init__(self, parent, app):
        QWidget.__init__(self, parent)
        self.parent = parent
        self.app = app
        self.image=None
        self.setGeometry(
            QRect(0, 0, self.parent.width(), self.parent.height()))
        self.largeur = self.parent.width()
        self.hauteur = self.parent.height()
        self.setAutoFillBackground(False)
        self.p1 = vecteur()
        self.p2 = vecteur()
        self.pos_echelle = vecteur()
        self.cible_icon = os.path.join(
            self.app._dir("icones"), "curseur_cible.svg")
        pix = QPixmap(self.cible_icon).scaledToHeight(32, 32)
        self.cursor = QCursor(pix)
        self.setCursor(self.cursor)
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
            self.pos_echelle = vecteur(event.x(), event.y())
        self.app.zoom_zone.fait_crop(self.pos_echelle)

        if self.pressed:
            self.p2 = vecteur(event.x(), event.y())
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == 1 and self.p1.x >= 0:
            self.p2 = vecteur(event.x(), event.y())
        self.app.zoom_zone.fait_crop(vecteur(50,50))
        self.parent.index_du_point = 0

        self.app.video.echelle_image.p1 = self.p1.copy()
        self.app.video.echelle_image.p2 = self.p2.copy()

        #self.app.p1 = self.p1.copy()
        #self.app.p2 = self.p2.copy()
        epxParM = self.app.video.echelle_image.pxParM()
        self.app.affiche_echelle()
        # self.app.affiche_nb_points(True)
        self.app.mets_a_jour_widget_infos(self.app.tr(
            u"Choisir le nombre de points puis « Démarrer l'acquisition » "))
        self.app.mets_en_orange_echelle()

        # self.app.affiche_lance_capture(False)

        self.app.feedbackEchelle(self.p1, self.p2)
        self.app.change_axe_ou_origine()
        if len(self.app.listePoints) > 0:  # si on appelle l'échelle après avoir déjà pointé
            self.app.mets_a_jour_widget_infos(self.app.tr(
                "Vous pouvez continuer votre acquisition"))
            self.app.affiche_nb_points(False)
            self.app.refait_echelle()

        self.app.echelle_faite = True
        self.close()


class Echelle_TraceWidget(QWidget):
    def __init__(self, parent, p1, p2):
        QWidget.__init__(self, parent)
        self.parent = parent
        self.image = None
        self.setGeometry(
            QRect(0, 0, self.parent.width(), self.parent.height()))
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
            QRect(0, 0, self.parent.width(), self.parent.height()))

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
