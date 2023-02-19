# -*- coding: utf-8 -*-

"""
    etatsCoord, a module for pymecavideo:
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
        changement d'état : fait ce qu'il faut faire au niveau
        de l'onglet des coordonnées
        """
        self.etat = etat
        if etat == "debut":
            # décochage de widgets
            for obj in self.checkBox_Ec, self.checkBox_Em, self.checkBox_Epp:
                obj.setChecked(False)
        elif etat == "A":
            # décochage de widgets
            for obj in self.checkBox_Ec, self.checkBox_Em, self.checkBox_Epp:
                obj.setChecked(False)
        elif etat == "AB":
            pass
        elif etat == "C":
            pass
        elif etat == "D":
            # comme l'onglet 2 est actif, il faut s'occuper du statut des
            # boutons pour les énergies
            for obj in self.checkBox_Ec, self.checkBox_Em, self.checkBox_Epp:
                obj.setChecked(False)
                obj.setEnabled(bool(self.pointage.echelle_image))
            self.pushButton_select_all_table.setEnabled(True)
        elif etat == "E":
            pass
        return

