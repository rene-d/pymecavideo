# -*- coding: utf-8 -*-

"""
    pointageWidget, a module for pymecavideo:
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

import os

from vecteur import vecteur

class Etats(QObject):
    """
    Une classe qui permet de définir les états de l'application:
    debut, A, AB, B, C, D, E : voir le fichier etats_pymecavideo.html
    """

    def __init__(self):
        QObject.__init__(self)
        return

    def etatUI(self, etat):
        """
        Mise en place d'un état de l'interface utilisateur, voir la
        documentation dans le fichier etat_pymecavideo.html

        après l'état C, il faut tenir compte d'un ancien état, A*/D*
        """
        fonctions = { # fonctions de rappel pour chaque changement d'état
            "debut": self.etatDebut,
            "A":     self.etatA,
            "AB":    self.etatAB,
            "B":     self.etatB,
            "C":     self.etatC,
            "D":     self.etatD,
            "E":     self.etatE,
        }

        if self.etat == etat: return # inutile de changer !
        self.dbg.p(1, f"========> État précédent = {self.etat}. État suivant = {etat}")
        self.etat = etat
        if self.etat not in fonctions:
            raise Exception(
                f"L'état doit être {', '.join(list(fonctions.keys()))}, or il est « {repr(self.etat)} »")
        self.etat = etat
        # appel de la fonction liée à l'état courant
        fonctions[self.etat]()
        return
    
    def etatDebut(self):
        """
        On y arrive quand on lance pymecavideo, et qu’aucune vidéo
        n’est passée, ni par argument, ni par le fichier de
        configuration.

        Tous les onglets sont désactivés ; idéalement, une aide
        pour dire d’aller chercher un fichier vidéo apparaît.
        """
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
        return
        
    def etatA(self):
        """
        Une vidéo est connue et on en affiche une image.

        Le premier onglet est actif, on voit une image de la
        vidéo, les contrôles pour se déplacer dans le film sont
        actifs, on peut modifier le nombre d’objets à pointer, Le
        bouton Démarrer est visible et actif.

        Inutile de montrer le bouton de réinitialisation

        Sur l’image de la vidéo, le curseur est ordinaire.
        """
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
            
        return

    def etatAB(self):
        """
        On y arrive en cliquant sur le bouton démarrer, si la case
        à cocher « pointage auto » était cochée. On doit définir,
        par tirer-glisser à la souris, autant de zones
        rectangulaires à suivre qu’il y a d’objets à pointer.

        Le premier onglet est actif, mais tous les widgets de
        contrôle y sont inactifs.
        """
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
        return
        
    def etatB(self):
        """
        On y arrive quand les zones rectangulaires à suivre sont
        définies.

        Le premier onglet est actif, mais tous les widgets de contrôle
        y sont inactifs et on fait apparaître le bouton STOP
        """
        self.pushButton_stopCalculs.setText("STOP")
        self.pushButton_stopCalculs.setEnabled(True)
        self.pushButton_stopCalculs.show()
        self.update()
        # initialise la détection des points
        self.detecteUnPoint()
        return
    
    def etatC(self):
        """
        L’échelle est en cours de définition.

        Le premier onglet est actif, mais tous les boutons qu’on
        peut y voir sont inactifs jusqu’à la fin de la définition
        de l’échelle.

        Cet état peut se situer entre A et A, ou entre D et D,
        selon la valeur de self.etat_ancien.
        """
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
        
        return
        
    def etatD(self):
        """
        Une vidéo est connue et on en affiche une image.
        Le pointage a été démarré, manuellement, ou un pointage
        automatique vient de finir.Tous les onglets sont actifs.

        Les contrôles pour changer d’image sont actifs, et le seul
        autre bouton actif sur le premier onglet est celui qui
        permet de changer d’échelle. Dans tous les cas, le bouton STOP
        y est caché

        Le pointage n’est possible que dans deux cas :

        quand aucune image n’a été pointée quand le pointage à
        venir est voisin de pointages existants : sur une image
        déjà pointée, ou juste avant, ou juste après.

        Quand le pointage est possible et seulement alors, le
        curseur de souris a la forme d’une grosse cible ;
        idéalement il identifie aussi l’objet à pointer.
        """
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
        return

    def etatE(self):
        """
        On est en train de pointer une série d’objets pour la même date.
        Le curseur de souris a la forme d’une grosse cible ;
        idéalement il identifie aussi l’objet à pointer.

        Durant ce pointage, les contrôles de changement d’image
        sont inactifs, ainsi que les onglets autres que le
        premier.
        """
        self.label_zoom.emit(self.tr("Pointage ({obj}) ; x, y =").format(obj = self.objet_courant))
        self.imgControlImage(False)
        for i in 1, 2, 3:
            self.tabWidget.setTabEnabled(i, False)        
        return
        
    def restaureEtat(self):
        """
        Restauration de l'état A ou D après (re)définition de l'échelle
        """
        self.change_etat.emit(self.etat_ancien)
        return

    def definit_messages_statut(self):
        """
        Définit les correspondances en état et message de barre de statut
        """
        # les fonction qui permettent d'avoir les débuts de messages de statut
        def msgDebut(app):
            return self.tr("Début : ouvrez un fichier, ou un exemple des aides")
        def msgA(app):
            if app.filename is None: return ""
            return self.tr("Fichier vidéo : {filename} ... définissez l'échelle ou démarrez le pointage | Il est possible de redimensionner la fenêtre").format(filename = os.path.basename(app.filename))
        def msgAB(app):
            return self.tr("Préparation du pointage automatique : sélectionnez les objets à suivre, au nombre de {n}").format(n = app.pointage.nb_obj)
        def msgB(app):
            return self.tr("Pointage automatique en cours : il peut être interrompu par le bouton STOP")
        def msgC(app):
            return self.tr("Définissez l'échelle, par un tirer-glisser sur l'image")
        def msgD(app):
            return self.tr("Pointage manuel : cliquez sur le premier objet à suivre")
        def msgE(app):
            return self.tr("Pointage manuel : il reste encore des objets à pointer, on en est à {obj}").format(obj = app.pointage.objet_courant)
        return { # résumé de ce que représente un état
            "debut" : msgDebut,
            "A" :     msgA,
            "AB" :    msgAB,
            "B" :     msgB,
            "C" :     msgC,
            "D" :     msgD,
            "E" :     msgE,
        }
    
