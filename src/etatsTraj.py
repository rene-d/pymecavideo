# -*- coding: utf-8 -*-

"""
    etatsTraj, a module for pymecavideo:
      a program to track moving points in a video frameset
      
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

from PyQt6.QtCore import Qt, QObject, pyqtSignal, QTimer

import os

from vecteur import vecteur
from etats import Etats_Base

class Etats(Etats_Base):
    """
    Une classe qui permet de définir les états pour le ccordWidget
    debut, A, AB, B, C, D, E : voir le fichier etats_pymecavideo.html
    """

    def __init__(self):
        Etats_Base.__init__(self)
        return

    def changeEtat(self, etat):
        """
        actions à faire en cas de changement d'état
        @param etat : debut, A, AB, B, C, D, E
        """
        self.etat = etat
        if etat =="debut":
            for obj in self.button_video, self.widget_chronophoto:
                obj.setEnabled(False)
            # initialisation de self.trajW
            self.trajW.chrono = False
            # on cache certains widgets
            for obj in self.radioButtonNearMouse, \
                self.radioButtonSpeedEveryWhere:
                obj.hide()
        elif etat =="A":
            self.spinBox_chrono.setMaximum(self.pointage.image_max)
        elif etat =="AB":
            pass
        elif etat =="B":
            pass
        elif etat =="C":
            pass
        elif etat =="D":
            self.comboBox_referentiel.setEnabled(True)
            self.comboBox_referentiel.clear()
            self.comboBox_referentiel.insertItem(-1, "camera")
            for obj in self.pointage.suivis:
                self.comboBox_referentiel.insertItem(
                    -1, self.tr("objet N° {0}").format(str(obj)))
            pass
        elif etat =="E":
            pass
        return
