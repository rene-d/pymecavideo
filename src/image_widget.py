# -*- coding: utf-8 -*-
"""
    image_widget, a module for pymecavideo:
      a program to track moving points in a video frameset
      
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

from PyQt6.QtCore import QRect, Qt, QPointF
from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPixmap, QImage, QPainter, QPen, QColor

class ImageWidget(QWidget):
    """
    Un widget contenant une image

    Paramètres du constructeur :
    @param parent le widget parent, None par défaut
    @param image une image, None par défaut
    """

    def __init__(self, parent=None, image=None):
        QWidget.__init__(self, parent)
        self.setImage(image)

    def setImage(self, image=None, position=None):
        """
        définit l'image de fond
        """
        if not image:
            self.image = None
        elif isinstance(image, QPixmap):
            self.image = image
        elif isinstance(image, QImage):
            self.image = QPixmap.fromImage(image)
        if position is not None :
            dx = 90 if position.x > 100 else 228
            dy = -35
            self.move(int(position.x+dx), int(position.y+dy) )
        return

class Zoom(ImageWidget):
    """
    classe dédiée, qui permet d'avoir un zoom de 100x100 px sur un détail
    
    Paramètres du constructeur
    @param app la fenêtre prncipale
    @param parent le parent, None par défaut
    @param image l'image de fonf, None par défaut
    """

    def __init__(self, app=None, parent=None, image=None):
        ImageWidget.__init__(self, parent, image)
        self.app = app
        return

    def setApp(self, app):
        self.app = app
        return

    def fait_crop(self, image, p):
        """
        récupère une zone rectangulaire dans l'image affiché e
        (dans le widget vidéo) et l'affiche grandie deux fois.
        param image une image
        @param p un vecteur
        """
        if not image:
            return
        rect = QRect(round(p.x) - 25, round(p.y) - 25, 50, 50)
        crop = image.copy(rect)
        if isinstance(crop, QImage):
            cropX2 = QPixmap.fromImage(
                crop.scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio))
        else:
            cropX2 = crop.scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio)
        self.setImage(cropX2, p)
        return

    def paintEvent(self, event):
        if self.image : #TODO compléter les états possibles pour zoom (échelles etc.)
            painter = QPainter()
            painter.begin(self)
            if self.image != None:
                painter.drawPixmap(0, 0, self.image)
            #croix de visée
            painter.setPen(QColor("red"))
            painter.drawLine(50, 0, 50, 45)
            painter.drawLine(50, 55, 50, 100)
            painter.drawLine(0, 50, 45, 50)
            painter.drawLine(55, 50, 100, 50)

            #bordure extérieure
            #painter.setPen(QColor("yellow"))
            painter.drawLine(0, 0, 0, 100)
            painter.drawLine(0, 0, 100, 0)
            painter.drawLine(0, 100, 100, 100)
            painter.drawLine(100, 0, 100, 100)

            # fixe la couleur du crayon et la largeur pour le dessin - forme compactée
            painter.setPen(QPen(QColor(255, 64, 255), 1))
            # cf QPen(QBrush brush, float width, Qt.PenStyle style = Qt.SolidLine, Qt.PenCapStyle cap = Qt.SquareCap, Qt.PenJoinStyle join = Qt.BevelJoin)
            painter.drawEllipse(QPointF(50, 50), 5, 5)
            painter.end()
