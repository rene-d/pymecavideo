# -*- coding: utf-8 -*-

"""
    videoWidget, a module for pymecavideo:
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

from PyQt6.QtCore import QThread, pyqtSignal, QLocale, QTranslator, Qt, \
    QSize, QTimer, QObject, QRect, QPoint, QPointF
from PyQt6.QtGui import QKeySequence, QIcon, QPixmap, QImage, QPainter, \
    QCursor, QPen, QColor, QFont, QResizeEvent, QShortcut
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QLayout, \
    QFileDialog, QTableWidgetItem, QInputDialog, QLineEdit, QMessageBox, \
    QTableWidgetSelectionRange

import os, time, re
import locale

from version import Version
from vecteur import vecteur
from echelle import Echelle_TraceWidget
from image_widget import ImageWidget
from globdef import cible_icon, DOCUMENT_PATH, inhibe
from cadreur import openCvReader
from toQimage import toQImage

import interfaces.icon_rc

class VideoPointeeWidget(ImageWidget):
    """
    Cette classe permet de gérer une séquence d'images extraites d'une vidéo
    et les pointages qu'on peut réaliser à la souris ou automatiquement,
    pour suivre les mouvements d'un ou plusieurs objets.
    """

    def __init__(self, parent):
        ImageWidget.__init__(self, parent)
        self.setMouseTracking(True)     # on réagit aux mouvement de souris
        self.index = None          # index de l'image courante
        self.objet_courant = 1     # désignation de l'objet courant
        self.image_w = self.width()     # deux valeurs par défaut
        self.image_h = self.height()    # pas forcément pertinentes
        self.rotation = 0          # permet de retourner une vidéo mal prise
        self.setMouseTracking(True)
        self.couleurs = [
            "red", "blue", "cyan", "magenta", "yellow", "gray", "green"] *2
        return


    def __str__(self):
        """
        donne une vision partielle de l'instance courante
        """
        result = {a : str(getattr(self,a)) for a in dir(self) \
                  if not callable(getattr(self,a)) and \
                  not isinstance(getattr(self,a), QObject)}
        
        return f"VideoPointeeWidget({result})"
    
    def setParent(self, w):
        """
        Connecte le videoWidget au widget principal de son onglet,
        et son débogueur ; self.pw devient un pointeur vers ce widget
        @param w le widget principal de l'onglet de pointage
        """
        self.pw = w
        self.dbg = w.dbg
        return
   
    def clear(self):
        self.image = None
        return

    def resizeEvent(self, e):
        self.dbg.p(2, "rentre dans 'resizeEvent'")
        self.pw.update_imgedit.emit(
            self.image_w, self.image_h, self.rotation)
        if e.oldSize() != QSize(-1, -1):
            ratiow = self.width()/e.oldSize().width()
            ratioh = self.height()/e.oldSize().height()
            self.pw.update_origine.emit(ratiow, ratioh)
        return

    def leaveEvent(self, event):
        self.pw.disable_zoom.emit()

    def enterEvent(self, event):
        if self.pw.etat in ('C', 'D'):
            self.pw.remet_zoom.emit()


    def mouseReleaseEvent(self, event):
        """
        enregistre le point de l'évènement souris, si self.pointageOK
        est vrai ; voir self.extract_image pour voir les conditions
        de validité.

        Si self.refait_point est vrai (on a été délégué depuis un
        bouton refaire, du tableau de coordonnées, alors on rebascule
        éventuellement vers l'onglet coordonnées, quand le dernier
        objet a été pointé.
        """
        if event.button() == Qt.MouseButton.LeftButton:
            self.pw.fin_pointage_manuel.emit(event)
        return

    def mouseMoveEvent(self, event):
        if self.pw.etat in ( 'C' , 'D', 'E') :
            self.pw.remet_zoom.emit()
            self.pw.update_zoom.emit(vecteur(qPoint = event.position()))
        return

    def paintEvent(self, event):
        if self.image:
            painter = QPainter()
            painter.begin(self)
            ############################################################
            # mise en place de l'image
            if self.image is not None: painter.drawPixmap(0, 0, self.image)

            ############################################################
            # dessine les pointages passés
            self.dbg.p(
                5, "In videoWidget, paintEvent, self.pw.data :%s" % self.pw.data)
            if self.pw.data:
                for date in self.pw.data:
                    for obj in self.pw.data[date]:
                        point = self.pw.data[date][obj]
                        if point:
                            painter.setPen(QColor(self.couleurs[int(obj)-1]))
                            painter.setFont(QFont("", 10))
                            painter.translate(point.x, point.y)
                            painter.drawLine(-2, 0, 2, 0)
                            painter.drawLine(0, -2, 0, 2)
                            painter.translate(-10, +10)
                            painter.drawText(0, 0, str(obj))
                            painter.translate(-point.x + 10, -point.y - 10)

            ############################################################
            # dessine le repere
            painter.setPen(QColor("green"))
            painter.drawText(
                round(self.pw.origine.x) + 5, round(self.pw.origine.y) + 15, "O")
            painter.translate(0, 0)
            painter.translate(round(self.pw.origine.x), round(self.pw.origine.y))
            p1 = QPoint(round(self.pw.sens_X * (-40)), 0)
            p2 = QPoint(round(self.pw.sens_X * (40)), 0)
            p3 = QPoint(round(self.pw.sens_X * (36)), 2)
            p4 = QPoint(round(self.pw.sens_X * (36)), -2)
            painter.scale(1, 1)
            painter.drawPolyline(p1, p2, p3, p4, p2)
            painter.rotate(self.pw.sens_X * self.pw.sens_Y * (-90))
            painter.drawPolyline(p1, p2, p3, p4, p2)
            painter.end()
        return

    def placeImage(self, im, ratio, largeurFilm):
        """
        place une image dans le widget, en conservant le ratio de cette image
        @param im une image
        @param ratio le ratio à respecter
        @param largeurFilm la largeur originale de la video en pixel
        @return l'image, redimensionnée selon le ratio
        """
        self.dbg.p(2, "rentre dans 'placeImage'")
        self.image_w = min(self.width(), round(self.height() * ratio))
        self.image_h = round(self.image_w / ratio)
        self.echelle = self.image_w / largeurFilm
        self.setMouseTracking(True)
        image = im.scaled(self.image_w, self.image_h)
        self.setImage(image)
        self.update()
        return image
    
