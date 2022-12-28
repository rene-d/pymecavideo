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

from PyQt5.QtCore import QRect, Qt
from PyQt5.QtWidgets import QWidget, qApp
from PyQt5.QtGui import QPixmap, QImage, QPainter

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
        """
        if not image:
            self.image = None
        elif isinstance(image, QPixmap):
            self.image = image
        elif isinstance(image, QImage):
            self.image = QPixmap.fromImage(image)
        self.update()
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

    def fait_crop(self, p):
        """
        récupère une zone rectangulaire dans l'image affiché e
        (dans le widget vidéo) et l'affiche grandie deux fois.
        @param p un vecteur
        """
        rect = QRect(round(p.x) - 25, round(p.y) - 25, 50, 50)
        crop = self.app.imageAffichee.copy(rect)
        cropX2 = QPixmap.fromImage(
            crop.scaled(100, 100, Qt.KeepAspectRatio))
        self.setImage(cropX2)
        return

    def paintEvent(self, event):
        if self.app.a_une_image:
            self.painter = QPainter()
            self.painter.begin(self)
            if self.image != None:
                self.painter.drawPixmap(0, 0, self.image)
            self.painter.end()
