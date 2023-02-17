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

from PyQt6.QtCore import QObject
class Etats(QObject):
    """
    Une classe qui permet de définir les états de l'application:
    debut, A, AB, B, C, D, E : voir le fichier etats_pymecavideo.html
    """

    def __init__(self):
        QObject.__init__(self)
        return
    
    def definit_messages_statut(self):
        """
        Définit le début des messages à envoyer dans la ligne de statut;
        il s'agit de définir le dictionnaire self.roleEtat de structure
        etat => fonction de rappel pour renvoyer une chaîne appropriée
        """
        def msgDebut(app):
            return self.tr("Début : ouvrez un fichier, ou un exemple des aides")
        def msgA(app):
            return self.tr("Fichier vidéo : {filename} ... définissez l'échelle ou démarrez le pointage | Il est possible de redimensionner la fenêtre").format(filename = os.path.basename(app.pointage.filename))
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
        
        self.roleEtat = { # résumé de ce que représente un état
            "debut" : msgDebut,
            "A" :     msgA,
            "AB" :    msgAB,
            "B" :     msgB,
            "C" :     msgC,
            "D" :     msgD,
            "E" :     msgE,
        }
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
        self.setStatus("")
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
        for obj in self.actionDefaire, self.actionRefaire, \
            self.actionCopier_dans_le_presse_papier, self.menuE_xporter_vers, \
            self.actionSaveData, self.widget_chronophoto, self.pointage.spinBox_image, \
            self.pointage.pushButton_rot_droite, self.pointage.pushButton_rot_gauche, \
            self.pointage.pushButton_stopCalculs, \
            self.button_video, self.pointage.label_nb_de_points, \
            self.pointage.spinBox_objets, self.pointage.Bouton_Echelle, \
            self.pointage.checkBox_auto, self.pointage.Bouton_lance_capture, \
            self.pointage.pushButton_reinit, self.pointage.pushButton_origine, \
            self.pointage.pushButton_defait, self.pointage.pushButton_refait, \
            self.pointage.checkBox_abscisses, self.pointage.checkBox_ordonnees, \
            self.pointage.label_IPS, self.pointage.lineEdit_IPS :
            
            obj.setEnabled(False)
            
        # décochage de widgets
        for obj in self.checkBox_Ec, self.checkBox_Em, self.checkBox_Epp:
            obj.setChecked(False)
        
        # activation de widgets
        for obj in self.tabWidget, self.actionExemples:

            obj.setEnabled(True)

        # on cache certains widgets
        for obj in self.radioButtonNearMouse, \
            self.radioButtonSpeedEveryWhere, self.pointage.pushButton_stopCalculs:

            obj.hide()

        # organisation des onglets
        self.tabWidget.setCurrentIndex(0)       # montre l'onglet video
        for i in range(1,4):
            self.tabWidget.setTabEnabled(i, False)  # autres onglets inactifs

         # initialisation de self.trajectoire_widget
        self.trajectoire_widget.chrono = False

        # désactive les contôles de l'image
        self.imgControlImage(False)

        # marque "indéf." dans l'afficheur d'échelle à gauche
        self.affiche_echelle()

        # mise à jour de styles
        self.pointage.Bouton_Echelle.setStyleSheet("background-color:None;")

        # autorise le redimensionnement de la fenêtre principale
        self.OKRedimensionnement.emit()

        # inactive le spinner pour les incréments de plus d'une image
        # voir la demande de Isabelle.Vigneau@ac-versailles.fr, 15 Sep 2022
        # non encore implémentée
        self.pointage.imgno_incr.hide()
        self.pointage.spinBox.hide()

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
        self.setWindowTitle(self.tr("Pymecavideo : {filename}").format(
            filename = os.path.basename(self.pointage.filename)))
        self.pointage.objet_courant = 1
        self.label_zoom.emit(self.tr("Zoom autour de x, y ="))
        if not self.pointage.echelle_image:
            self.affiche_echelle() # marque "indéf."
            self.echelle_modif.emit(self.tr("Définir l'échelle"),
                                    "background-color:None;")
            # comme il n'y a pas d'échelle, on peut redimensionner la fenêtre
            self.OKRedimensionnement.emit()
            if self.pointage.echelle_trace:
                self.pointage.echelle_trace.hide()
        # ferme les widget d'affichages des x, y, v du 2eme onglet
        # si elles existent
        for plotwidget in self.dictionnairePlotWidget.values():
            plotwidget.parentWidget().close()
            plotwidget.close()
            del plotwidget
        self.init_variables(self.pointage.filename)
        # active les contrôle de l'image, montre l'image
        self.imgControlImage(True)
        self.pointage.affiche_image()
        # réactive plusieurs widgets
        for obj in self.pointage.label_nb_de_points, self.pointage.pushButton_reinit, \
            self.pointage.spinBox_objets, self.pointage.Bouton_Echelle, \
            self.pointage.checkBox_auto, self.pointage.Bouton_lance_capture, \
            self.pointage.pushButton_origine, self.actionCopier_dans_le_presse_papier, \
            self.pointage.checkBox_abscisses, self.pointage.checkBox_ordonnees, \
            self.pointage.label_IPS, self.pointage.lineEdit_IPS, \
            self.menuE_xporter_vers, self.actionSaveData :

            obj.setEnabled(True)

        # si une échelle est définie, on interdit les boutons de rotation
        # sinon on autorise ces boutons
        rotation_possible = not self.pointage.echelle_image
        for obj in self.pointage.pushButton_rot_droite, self.pointage.pushButton_rot_gauche :
            obj.setEnabled(rotation_possible)
                
        # ajuste le nombre d'objets suivis
        if self.pointage.suivis:
            self.pointage.spinBox_objets.setValue(self.pointage.nb_obj)
        else:
            self.pointage.dimension_data.emit(1)
            self.pointage.spinBox_objets.setValue(1)

        # desactive d'autres widgets
        self.pointage.pushButton_stopCalculs.setEnabled(False)
        self.pointage.pushButton_stopCalculs.hide()
        self.enableDefaire(False)
        self.enableRefaire(False)
        self.pointage.checkBox_abscisses.setCheckState(Qt.CheckState.Unchecked)
        self.pointage.checkBox_ordonnees.setCheckState(Qt.CheckState.Unchecked)
        self.pointage.checkBox_auto.setCheckState(Qt.CheckState.Unchecked)
        for i in 1, 2, 3:
            self.tabWidget.setTabEnabled(i, False)
        self.checkBox_Ec.setChecked(False)
        self.checkBox_Em.setChecked(False)
        self.checkBox_Epp.setChecked(False)
        
        # désactive le grapheur si existant
        if self.graphWidget:
            plotItem = self.graphWidget.getPlotItem()
            plotItem.clear()
            plotItem.setTitle('')
            plotItem.hideAxis('bottom')
            plotItem.hideAxis('left')
 
        """
        Prépare une session de pointage, au niveau de la
        fenêtre principale, et met à jour les préférences
        """
        d = self.prefs.defaults
        d['lastVideo'] = self.pointage.filename
        d['videoDir'] = os.path.dirname(self.pointage.filename)
        d["taille_image"] = f"({self.pointage.image_w},{self.pointage.image_h})"
        d['rotation'] = str(self.pointage.rotation)
        self.prefs.save()

        self.pointage.spinBox_image.setMinimum(1)
        self.pointage.spinBox_image.setValue(1)
        self.spinBox_chrono.setMaximum(self.pointage.image_max)
        self.pointage.spinBox_objets.setEnabled(True)
        self.tab_traj.setEnabled(0)

        self.affiche_statut.emit(
           self.tr("Veuillez choisir une image (et définir l'échelle)"))
        self.montre_vitesses = False
        self.egalise_origine()
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
            self.spinBox_objets, self.pointage.Bouton_Echelle, \
            self.checkBox_auto, self.Bouton_lance_capture, \
            self.pushButton_origine, self.actionCopier_dans_le_presse_papier, \
            self.checkBox_abscisses, self.checkBox_ordonnees, \
            self.label_IPS, self.lineEdit_IPS, \
            self.menuE_xporter_vers, self.actionSaveData :

            obj.setEnabled(False)

        QMessageBox.information(
            None, "Capture Automatique",
            self.tr("""\
            Veuillez sélectionner un cadre autour du ou des objets que vous voulez suivre.
            Vous pouvez arrêter à tout moment la capture en appuyant sur le bouton STOP""",None))
        self.affiche_statut.emit(self.tr("Pointage Automatique"))
        self.imgControlImage(False)
        # on démarre la définition des zones à suivre
        self.pointage.capture_auto()
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
        self.pointage.detecteUnPoint()
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
        for obj in self.pointage.pushButton_rot_droite, self.pointage.pushButton_rot_gauche, \
            self.pointage.label_nb_de_points, \
            self.pointage.spinBox_objets, self.pointage.Bouton_Echelle, \
            self.pointage.checkBox_auto, self.pointage.Bouton_lance_capture, \
            self.pointage.pushButton_origine, self.actionCopier_dans_le_presse_papier, \
            self.pointage.checkBox_abscisses, self.pointage.checkBox_ordonnees, \
            self.pointage.label_IPS, self.pointage.lineEdit_IPS, \
            self.menuE_xporter_vers, self.actionSaveData :

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
        self.label_zoom.emit(self.tr("Pointage ({obj}) ; x, y =").format(obj = self.pointage.suivis[0]))
        # empêche de redimensionner la fenêtre
        self.stopRedimensionnement.emit()
        # prépare le widget video
        self.pointage.setFocus()
        if self.pointage.echelle_trace: self.pointage.echelle_trace.lower()
        # on cache le bouton STOP
        self.pointage.pushButton_stopCalculs.setEnabled(False)
        self.pointage.pushButton_stopCalculs.hide()
        # on force extract_image afin de mettre à jour le curseur de la vidéo
        self.pointage.extract_image(self.pointage.horizontalSlider.value())
        
        self.pointage.affiche_point_attendu(self.pointage.suivis[0])
        self.pointage.lance_capture = True
         # les widgets de contrôle de l'image sont actifs ici
        self.imgControlImage(True)
        
        # tous les onglets sont actifs
        for i in 1, 2, 3:
            self.tabWidget.setTabEnabled(i, True)
            
        # comme l'onglet 2 est actif, il faut s'occuper du statut des
        # boutons pour les énergies !
        for obj in self.checkBox_Ec, self.checkBox_Em, self.checkBox_Epp:
            obj.setChecked(False)
            obj.setEnabled(bool(self.pointage.echelle_image))
            
        # mise à jour des menus
        self.actionSaveData.setEnabled(True)
        self.actionCopier_dans_le_presse_papier.setEnabled(True)
        self.comboBox_referentiel.setEnabled(True)
        self.pushButton_select_all_table.setEnabled(True)

        self.comboBox_referentiel.clear()
        self.comboBox_referentiel.insertItem(-1, "camera")
        for obj in self.pointage.suivis:
            self.comboBox_referentiel.insertItem(
                -1, self.tr("objet N° {0}").format(str(obj)))

        # désactive des boutons et des cases à cocher
        for obj in self.pointage.pushButton_origine, self.pointage.checkBox_abscisses, \
            self.pointage.checkBox_ordonnees, self.pointage.checkBox_auto, \
            self.pointage.Bouton_lance_capture, self.pointage.pushButton_rot_droite, \
            self.pointage.pushButton_rot_gauche :

            obj.setEnabled(False)

        # si aucune échelle n'a été définie, on place l'étalon à 1 px pour 1 m.
        if self.pointage.echelle_image.mParPx() == 1:
            self.pointage.echelle_image.longueur_reelle_etalon = 1
            self.pointage.echelle_image.p1 = vecteur(0, 0)
            self.pointage.echelle_image.p2 = vecteur(0, 1)

        # active le bouton de réinitialisation
        self.pointage.pushButton_reinit.setEnabled(True)
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
        self.label_zoom.emit(self.tr("Pointage ({obj}) ; x, y =").format(obj = self.pointage.objet_courant))
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
        
    
