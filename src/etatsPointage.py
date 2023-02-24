# -*- coding: utf-8 -*-

"""
    etatsPointage, a module for pymecavideo:
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
    Une classe qui permet de définir les états pour le pointageWidget
    debut, A, AB, B, C, D, E : voir le fichier etats_pymecavideo.html
    """

    def __init__(self):
        Etats_Base.__init__(self)
        return

    def changeEtat(self, etat):
        """
        Mise en place d'un état de l'interface utilisateur, voir la
        documentation dans le fichier etat_pymecavideo.html

        après l'état C, il faut tenir compte d'un ancien état, A*/D*
        """
        self.etat = etat
        if etat =="debut":
            self.label_zoom.emit(self.tr("Zoom autour de x, y ="))
            # désactivation de widgets
            for obj in self.spinBox_image, \
                self.pushButton_rot_droite, self.pushButton_rot_gauche, \
                self.pushButton_stopCalculs, \
                self.label_nb_de_points, \
                self.spinBox_objets, self.Bouton_Echelle, \
                self.checkBox_auto, self.Bouton_lance_capture, \
                self.pushButton_reinit, self.pushButton_origine, \
                self.pushButton_defait, self.pushButton_refait, \
                self.checkBox_abscisses, self.checkBox_ordonnees, \
                self.label_IPS, self.lineEdit_IPS :

                obj.setEnabled(False)

            # met à 1 les contrôles de l'image
            self.spinBox_image.setValue(1)
            self.horizontalSlider.setMinimum(1)
            self.horizontalSlider.setMaximum(10)
            self.horizontalSlider.setValue(1)
            
            # désactive les contôles de l'image
            self.imgControlImage(False)

            # marque "indéf." dans l'afficheur d'échelle à gauche
            self.affiche_echelle()

            # mise à jour de styles
            self.Bouton_Echelle.setStyleSheet("background-color:None;")

            self.pushButton_stopCalculs.hide()
            # inactive le spinner pour les incréments de plus d'une image
            # voir la demande de Isabelle.Vigneau@ac-versailles.fr, 15 Sep 2022
            # non encore implémentée
            self.imgno_incr.hide()
            self.spinBox.hide()
        if etat =="A":
            self.objet_courant = 1
            self.label_zoom.emit(self.tr("Zoom autour de x, y ="))
            if not self.echelle_image:
                self.affiche_echelle() # marque "indéf."
                self.echelle_modif.emit(self.tr("Définir l'échelle"),
                                        "background-color:None;")
                if self.echelle_trace:
                    self.echelle_trace.hide()
            # active les contrôle de l'image, montre l'image
            self.imgControlImage(True)
            self.affiche_image()
            # réactive plusieurs widgets
            for obj in self.label_nb_de_points, self.pushButton_reinit, \
                self.spinBox_objets, self.Bouton_Echelle, \
                self.checkBox_auto, self.Bouton_lance_capture, \
                self.pushButton_origine, \
                self.checkBox_abscisses, self.checkBox_ordonnees, \
                self.label_IPS, self.lineEdit_IPS, self.spinBox_objets :

                obj.setEnabled(True)

            # si une échelle est définie, on interdit les boutons de rotation
            # sinon on autorise ces boutons
            rotation_possible = not self.echelle_image
            for obj in self.pushButton_rot_droite, self.pushButton_rot_gauche :
                obj.setEnabled(rotation_possible)

            # ajuste le nombre d'objets suivis
            if self.suivis:
                self.spinBox_objets.setValue(self.nb_obj)
            else:
                self.dimension_data.emit(1)
                self.spinBox_objets.setValue(1)

            # desactive d'autres widgets
            self.pushButton_stopCalculs.setEnabled(False)
            self.pushButton_stopCalculs.hide()
            self.enableDefaire(False)
            self.enableRefaire(False)
            self.checkBox_abscisses.setCheckState(Qt.CheckState.Unchecked)
            self.checkBox_ordonnees.setCheckState(Qt.CheckState.Unchecked)
            self.checkBox_auto.setCheckState(Qt.CheckState.Unchecked)
            """
            Prépare une session de pointage, au niveau de la
            fenêtre principale, et met à jour les préférences
            """
            d = self.prefs.defaults
            d['lastVideo'] = self.filename
            d['videoDir'] = os.path.dirname(self.filename)
            d["taille_image"] = f"({self.video.image_w},{self.video.image_h})"
            d['rotation'] = str(self.video.rotation)
            self.prefs.save()
        if etat =="AB":
            self.label_zoom.emit(self.tr("Zoom autour de x, y ="))
            # désactive plusieurs widgets
            for obj in self.pushButton_rot_droite, self.pushButton_rot_gauche, \
                self.label_nb_de_points, \
                self.spinBox_objets, self.Bouton_Echelle, \
                self.checkBox_auto, self.Bouton_lance_capture, \
                self.pushButton_origine, \
                self.checkBox_abscisses, self.checkBox_ordonnees, \
                self.label_IPS, self.lineEdit_IPS :

                obj.setEnabled(False)

            self.imgControlImage(False)
            # on démarre la définition des zones à suivre
            self.capture_auto()
        if etat =="B":
            self.pushButton_stopCalculs.setText("STOP")
            self.pushButton_stopCalculs.setEnabled(True)
            self.pushButton_stopCalculs.show()
            self.update()
            # initialise la détection des points
            self.detecteUnPoint()
        if etat =="C":
            # on prévoit un retour à l'état A ou D selon celui où on
            # commence à définir l'échelle
            self.etat_ancien = self.app.etat_ancien
            self.label_zoom.emit(self.tr("Zoom autour de x, y ="))
            # désactive plusieurs widgets
            for obj in self.pushButton_rot_droite, self.pushButton_rot_gauche, \
                self.label_nb_de_points, \
                self.spinBox_objets, self.Bouton_Echelle, \
                self.checkBox_auto, self.Bouton_lance_capture, \
                self.pushButton_origine, \
                self.checkBox_abscisses, self.checkBox_ordonnees, \
                self.label_IPS, self.lineEdit_IPS:

                obj.setEnabled(False)
        if etat =="D":
            self.label_zoom.emit(self.tr("Pointage ({obj}) ; x, y =").format(obj = self.suivis[0]))
            # empêche de redimensionner la fenêtre
            self.app.stopRedimensionnement.emit()
            # prépare le widget video
            self.setFocus()
            if self.echelle_trace: self.echelle_trace.lower()
            # on cache le bouton STOP
            self.pushButton_stopCalculs.setEnabled(False)
            self.pushButton_stopCalculs.hide()
            # on force extract_image afin de mettre à jour le curseur de la vidéo
            self.extract_image(self.horizontalSlider.value())

            self.affiche_point_attendu(self.suivis[0])
            self.lance_capture = True
             # les widgets de contrôle de l'image sont actifs ici
            self.imgControlImage(True)

           # désactive des boutons et des cases à cocher
            for obj in self.pushButton_origine, self.checkBox_abscisses, \
                self.checkBox_ordonnees, self.checkBox_auto, \
                self.Bouton_lance_capture, self.pushButton_rot_droite, \
                self.pushButton_rot_gauche :

                obj.setEnabled(False)

            # si aucune échelle n'a été définie, on place l'étalon à 1 px pour 1 m.
            if self.echelle_image.mParPx() == 1:
                self.echelle_image.longueur_reelle_etalon = 1
                self.echelle_image.p1 = vecteur(0, 0)
                self.echelle_image.p2 = vecteur(0, 1)

            # active le bouton de réinitialisation
            self.pushButton_reinit.setEnabled(True)
            self.extract_image(self.index)
        if etat =="E":
            self.label_zoom.emit(self.tr("Pointage ({obj}) ; x, y =").format(obj = self.objet_courant))
            self.imgControlImage(False)
        return
    
    def restaureEtat(self):
        """
        Restauration de l'état A ou D après (re)définition de l'échelle
        """
        self.app.change_etat.emit(self.etat_ancien)
        return

