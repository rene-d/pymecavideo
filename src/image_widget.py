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

from vecteur import vecteur

ZOOM_DIM = 100 # dimension de la zone de zoom (100×100 si c'est un carré)

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

    def setImage(self, image=None):
        """
        définit l'image de fond
        @param image l'image à mettre en fond (None par défaut)
        """
        if not image:
            self.image = None
        elif isinstance(image, QPixmap):
            self.image = image
        elif isinstance(image, QImage):
            self.image = QPixmap.fromImage(image)
        return

class Zoom(ImageWidget):
    """
    classe dédiée, qui permet d'avoir un zoom de ZOOM_DIMxZOOM_DIM px sur un détail
    
    Paramètres du constructeur
    @param app la fenêtre prncipale
    @param parent le parent, None par défaut
    @param image l'image de fonf, None par défaut
    """

    def __init__(self, app=None, parent=None, image=None):
        ImageWidget.__init__(self, parent, image)
        self.app = app
        return

    def setImage(self, image=None, position=None):
        """
        surcharge la méthode héritée de ImageWidget, en ajoutant un fonction
        de dessin décalée.
        @param image l'image à mettre en fond (None par défaut)
        @param position un point (None par défaut) ; si la position est
           renseignée, alors l'image est décalée ; c'est utile pour
           dessiner l'image zoomée à côté de la position du curseur.
        """
        ImageWidget.setImage(self, image)
        if position is not None :
            decale = position + vecteur(
                ZOOM_DIM+58, # decalage horizontal pour centrer sur le pointeur
                -45)         # decalage vertical pour mettre au-dessus
            self.move(int(decale.x), int(decale.y) )
        return
       

    def setApp(self, app):
        self.app = app
        return

    def fait_crop(self, image, p):
        """
        récupère une zone rectangulaire dans l'image affiché e
        (dans le widget vidéo) et l'affiche grandie deux fois.
        @param image une image
        @param p un vecteur
        """
        if not image:
            return
        imgsize = image.size()
        # on délimite un rectangle autour de p, de largeur/longueur
        # au plus ZOOM_DIM//2, mais limité par les frontières de l'image
        x1 = max(round(p.x) - ZOOM_DIM//4, 0)
        y1 = max(round(p.y) - ZOOM_DIM//4, 0)
        x2 = min(round(p.x) + ZOOM_DIM//4, imgsize.width())
        y2 = min(round(p.y) + ZOOM_DIM//4, imgsize.height())
        crop = image.copy(QRect(x1, y1, x2-x1, y2-y1))
        cropX2 = QImage(ZOOM_DIM, ZOOM_DIM, QImage.Format.Format_RGB888)
        cropX2.fill(QColor(255,255,255,255)) # blanc 100% transparent
        painter =  QPainter()
        painter.begin(cropX2)
        # pour dessiner l'image crop, il y a un décalage en x ou en y
        # dès lors que x1 ou y1 sont nuls ; la valeur absolue pourvoit
        # à ce décalage conditionnel.
        painter.drawPixmap(
            2 * abs(round(p.x) - ZOOM_DIM//4 - x1),
            2 * abs(round(p.y) - ZOOM_DIM//4 - y1),
            crop.scaled(
                ZOOM_DIM, ZOOM_DIM, Qt.AspectRatioMode.KeepAspectRatio))
        painter.end()
        self.setImage(cropX2, p)
        return

    def paintEvent(self, event):
        if self.image : #TODO compléter les états possibles pour zoom (échelles etc.)
            painter = QPainter()
            painter.begin(self)
            if self.image != None:
                painter.drawPixmap(0, 0, self.image)
            #croix de visée
            R = ZOOM_DIM//20 # rayon du cercle intérieur
            painter.setPen(QColor("red"))
            painter.drawLine(ZOOM_DIM//2, 0,
                             ZOOM_DIM//2, ZOOM_DIM//2-R)
            painter.drawLine(ZOOM_DIM//2, ZOOM_DIM//2+R,
                             ZOOM_DIM//2, ZOOM_DIM)
            painter.drawLine(0, ZOOM_DIM//2,
                             ZOOM_DIM//2-R, ZOOM_DIM//2)
            painter.drawLine(ZOOM_DIM//2+R, ZOOM_DIM//2,
                             ZOOM_DIM, ZOOM_DIM//2)

            #bordure extérieure
            #painter.setPen(QColor("yellow"))
            painter.drawLine(0, 0, 0, ZOOM_DIM-1)
            painter.drawLine(0, 0, ZOOM_DIM-1, 0)
            painter.drawLine(0, ZOOM_DIM-1, ZOOM_DIM-1, ZOOM_DIM-1)
            painter.drawLine(ZOOM_DIM-1, 0, ZOOM_DIM-1, ZOOM_DIM-1)

            # fixe la couleur du crayon et la largeur pour le dessin - forme compactée
            painter.setPen(QPen(QColor(255, 64, 255), 1))
            # cf QPen(QBrush brush, float width, Qt.PenStyle style = Qt.SolidLine, Qt.PenCapStyle cap = Qt.SquareCap, Qt.PenJoinStyle join = Qt.BevelJoin)
            painter.drawEllipse(QPointF(ZOOM_DIM//2, ZOOM_DIM//2), R, R)
            painter.end()
        return
    
