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

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from vecteur import vecteur
from zoom import Zoom_Croix


class echelle(QObject):
    def __init__(self, p1=vecteur(0, 0), p2=vecteur(0, 0)):
        self.p1, self.p2 = p1, p2
        self.longueur_reelle_etalon = 1

    def __str__(self):
        return "echelle(%s,%s,%s m)" % (self.p1, self.p2, self.longueur_reelle_etalon)

    def longueur_pixel_etalon(self):
        return (self.p1 - self.p2).norme()

    def isUndef(self):
        """
        Vrai si l'échelle n'est pas définie, c'est à dire si
        p1 et p2 sont confondus.
        """
        return (self.p1 - self.p2).norme() == 0

    def mParPx(self):
        """renvoie le nombre de mètre par pixel"""
        return self.longueur_reelle_etalon / self.longueur_pixel_etalon()

    def pxParM(self):
        """renvoie le nombre de pixel par mètre"""
        return self.longueur_pixel_etalon() / self.longueur_reelle_etalon

    def applique_echelle(self, pos):
        """
        les positions pos sont en pixels, ça renvoie une liste
        de positions (vecteurs) en mètre.
        """
        result = []
        for p in pos:
            result.append((vecteur(0, 480) - p) * self.mParPx())
        return result

    def etalonneReel(self, l):
        """
        Définit la longueur en mètre de l'étalon
        @param l longueur en mètre
        """
        self.longueur_reelle_etalon = float(l)


class Label_Echelle(QLabel):
    def __init__(self, parent, app):
        QLabel.__init__(self, parent)
        self.parent = parent
        self.setGeometry(QRect(0, 0, 640, 480))
        self.setAutoFillBackground(False)
        self.p1 = vecteur()
        self.p2 = vecteur()
        self.app = app
        self.setCursor(Qt.CrossCursor)
        self.cropX2 = None
        self.zoom_croix = Zoom_Croix(self.app.ui.label_zoom, self.app)
        self.zoom_croix.hide()
        self.setMouseTracking(True)
        self.pressed = False
        try:
            self.app.origine_trace.lower()  # origine definition is optionnal but hide scale if defined first
        except AttributeError:
            pass
        try:
            self.app.label_echelle_trace.hide()
            del self.app.label_echelle_trace
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
        if self.p1.x() > 0:
            painter.drawLine(self.p1.x(), self.p1.y(), self.p2.x(), self.p2.y())
        painter.end()

    def mouseMoveEvent(self, event):
        self.zoom_croix.show()
        self.pos = vecteur(event.x(), event.y())
        self.fait_crop(self.pos)
        self.app.ui.label_zoom.setPixmap(self.cropX2)

        if self.pressed:
            self.p2 = vecteur(event.x() + 1, event.y() + 1)
            self.update()

    def fait_crop(self, p):
        rect = QRect(p.x() - 25, p.y() - 25, 50, 50)
        crop = self.app.imageAffichee.copy(rect)
        self.cropX2 = QPixmap.fromImage(crop.scaled(100, 100, Qt.KeepAspectRatio))

    def mouseReleaseEvent(self, event):
        if event.button() == 1 and self.p1.x() >= 0:
            self.p2 = vecteur(event.x() + 1, event.y() + 1)
        self.zoom_croix.hide()
        self.app.ui.label_zoom.setPixmap(QPixmap(None))
        del self.zoom_croix
        self.parent.index_du_point = 0

        self.app.echelle_image.p1 = self.p1.copy()
        self.app.echelle_image.p2 = self.p2.copy()
        self.app.p1 = self.p1.copy()
        self.app.p2 = self.p2.copy()
        epxParM = self.app.echelle_image.pxParM()
        self.app.affiche_echelle()
        # self.app.affiche_nb_points(True)
        self.app.mets_a_jour_label_infos(self.app.tr(u"Choisir le nombre de points puis « Démarrer l'acquisition » "))

        self.app.affiche_lance_capture(True)
        self.app.feedbackEchelle(self.p1, self.p2)
        if len(self.app.tousLesClics) > 0:  #si on appelle l'échelle après avoir déjà pointé
            self.app.mets_a_jour_label_infos(self.app.tr("Vous pouvez continuer votre acquisition"))
            self.app.affiche_nb_points(False)
            self.app.refait_echelle()

        self.app.echelle_faite = True
        self.close()


class Label_Echelle_Trace(QLabel):
    def __init__(self, parent, p1, p2):
        QLabel.__init__(self, parent)
        self.parent = parent
        self.setGeometry(QRect(0, 0, 640, 480))
        self.setAutoFillBackground(False)
        self.p1 = p1
        self.p2 = p2
        self.setMouseTracking(True)

    def mouseMoveEvent(self, event):
        event.ignore()

    def mouseReleaseEvent(self, event):
        event.ignore()

    def paintEvent(self, event):
        painter = QPainter()
        painter.begin(self)
        painter.setPen(Qt.green)
        painter.drawLine(self.p1.x(), self.p1.y(), self.p2.x(), self.p2.y())
        painter.end()

