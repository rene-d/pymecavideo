# -*- coding: utf-8 -*-

"""
    pointageWidget, a module for pymecavideo:
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

import os, time, re, sys
import locale

from version import Version
from vecteur import vecteur
from echelle import Echelle_TraceWidget
from image_widget import ImageWidget
from pointage import Pointage
from globdef import cible_icon, DOCUMENT_PATH, inhibe
from cadreur import openCvReader
from toQimage import toQImage
from suivi_auto import SelRectWidget
from detect import filter_picture
from dbg import Dbg

import interfaces.icon_rc

from interfaces.Ui_pointage import Ui_pointageWidget

class PointageWidget(QWidget, Ui_pointageWidget):
    """
    Une classe qui affiche l'image d'une vidéo et qui gère le pointage
    d'objets mobiles dans cette vidéo. Elle gère les données de pointage
    et celles liées aux échelles de temps et d'espace

    paramètres du constructeur :
    @param parent un QWidget parent
    @param verbosite entre 1 et 3 pour les messages de débogage
    """

    def __init__(self, parent, verbosite = 0):
        self.dbg = Dbg(verbosite)
        QWidget.__init__(self, parent)
        Ui_pointageWidget.__init__(self)
        self.setupUi(self)
        self.video.setApp(self)
        self.zoom_zone.setApp(self)
        self.connecte_signaux()
        return

    ########### signaux #####################
    update_imgedit = pyqtSignal(int, int, int) # met à jour la dimension d'image
    ########### connexion des signaux #######
    def connecte_signaux(self):
        self.update_imgedit.connect(self.affiche_imgsize)
        return

    def affiche_imgsize(self, w, h, r):
        """
        Affiche la taille de l'image
        @param w largeur de l'image
        @param h hauteur de l'image
        @param r rotation de l'image
        """
        self.imgdimEdit.setText(f"{w} x {h} ({r}°)")
        return
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    verbosite = 1
    window = PointageWidget(None, verbosite)
    window.show()
    sys.exit(app.exec())
    
