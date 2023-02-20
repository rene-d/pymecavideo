# -*- coding: utf-8 -*-

"""
    etatsMain, a module for pymecavideo:
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

from PyQt6.QtCore import Qt, QObject, pyqtSignal
from PyQt6.QtWidgets import QMessageBox

import os

from vecteur import vecteur
from etats import Etats_Base

class Etats(Etats_Base):
    """
    Une classe qui permet de définir les états pour le pointageWidget
    debut, A, AB, B, C, D, E : voir le fichier etats_pymecavideo.html
    """

    def __init__(self):
        Etats_Base.__init__(self)
        return

    def changeEtat(self, etat):
        """
        changement d'état : fait ce qu'il faut faire au niveau de la fenêtre
        principale puis renvoie aux autres widgets actifs
        """
        self.setStatus("")
        self.etat_ancien = self.etat # conserve pour plus tard
        self.etat = etat
        self.dbg.p(1, f"========> État précédent = {self.etat_ancien}. État suivant = {self.etat}")
        if self.etat not in self.etats:
            raise Exception(
                f"L'état doit être {', '.join(self.etats)}, or il est « {repr(self.etat)} »")
        if etat == "debut":
            for obj in self.actionDefaire, self.actionRefaire, \
                self.actionCopier_dans_le_presse_papier, \
                self.menuE_xporter_vers, \
                self.actionSaveData :

                obj.setEnabled(False)
            self.actionExemples.setEnabled(True)
            self.tabWidget.setEnabled(True)
            # organisation des onglets
            self.tabWidget.setCurrentIndex(0)       # montre l'onglet video
            for i in range(1,4):
                self.tabWidget.setTabEnabled(i, False)  # autres onglets inactifs

            # autorise le redimensionnement de la fenêtre principale
            self.OKRedimensionnement.emit()

        elif etat == "A":
            if self.pointage.filename is None: return
            self.setWindowTitle(self.tr("Pymecavideo : {filename}").format(
                filename = os.path.basename(self.pointage.filename)))
            if not self.pointage.echelle_image:
                # sans échelle, on peut redimensionner la fenêtre
                self.OKRedimensionnement.emit()
            for obj in self.menuE_xporter_vers, self.actionSaveData, \
                self.actionCopier_dans_le_presse_papier:
                obj.setEnabled(True)
            for i in 1, 2, 3:
                self.tabWidget.setTabEnabled(i, False)
                
            self.affiche_statut.emit(
               self.tr("Veuillez choisir une image (et définir l'échelle)"))
            self.montre_vitesses = False
            self.egalise_origine()
            self.init_variables(self.pointage.filename)
            
        elif etat == "AB":
            for obj in self.actionCopier_dans_le_presse_papier, \
                self.menuE_xporter_vers, self.actionSaveData :
                obj.setEnabled(False)
            self.affiche_statut.emit(self.tr("Pointage Automatique"))
            QMessageBox.information(
                None, "Capture Automatique",
                self.tr("""\
Veuillez sélectionner un cadre autour du ou des objets que vous voulez suivre ;
Vous pouvez arrêter à tout moment la capture en appuyant sur le bouton STOP""",
                        None))
                
            pass
        elif etat == "B":
            pass
        elif etat == "C":
            for obj in self.actionCopier_dans_le_presse_papier, \
                self.menuE_xporter_vers, self.actionSaveData:
                obj.setEnabled(False)

        elif etat == "D":
            # tous les onglets sont actifs
            if self.pointage:
                for i in 1, 2, 3:
                    self.tabWidget.setTabEnabled(i, True)
            # mise à jour des menus
            self.actionSaveData.setEnabled(True)
            self.actionCopier_dans_le_presse_papier.setEnabled(True)

        elif etat == "E":
            for i in 1, 2, 3:
                self.tabWidget.setTabEnabled(i, False)        

        self.affiche_statut.emit("")
        for widget in self.pointage, self.trajectoire, self.coord, self.graph:
            widget.changeEtat(etat)
        return
