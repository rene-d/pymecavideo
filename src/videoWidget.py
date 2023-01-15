# -*- coding: utf-8 -*-

"""
    videoWidget, a module for pymecavideo:
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

from PyQt5.QtCore import QThread, pyqtSignal, QLocale, QTranslator, Qt, QSize, QTimer, QObject, QRect, QPoint, QPointF
from PyQt5.QtGui import QKeySequence, QIcon, QPixmap, QImage, QPainter, QCursor, QPen, QColor, QFont, QResizeEvent
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QShortcut, QDesktopWidget, QLayout, QFileDialog, QTableWidgetItem, QInputDialog, QLineEdit, QMessageBox, QTableWidgetSelectionRange

import os, time, re
import locale

from vecteur import vecteur
from echelle import echelle, Echelle_TraceWidget, EchelleWidget
from image_widget import ImageWidget
from pointage import Pointage
from globdef import _translate, beauGrosCurseur, DOCUMENT_PATH
from cadreur import openCvReader
from toQimage import toQImage
from suivi_auto import SelRectWidget
from detect import filter_picture

import icon_rc

class VideoPointeeWidget(ImageWidget, Pointage):
    """
    Cette classe permet de gérer une séquence d'images extraites d'une vidéo
    et les pointages qu'on peut réaliser à la souris ou automatiquement,
    pour suivre les mouvements d'un ou plusieurs objets.
    """

    def __init__(self, parent):
        #ImageWidget.__init__(self, parent)
        Pointage.__init__(self)
        self.app = None        # pointeur vers la fenêtre principale
        self.zoom = None       # pointeur vers le widget de zoom
        self.hotspot = None    # vecteur (position de la souris)
        pix = QPixmap(":/data/icones/curseur_cible.svg").scaledToHeight(32, 32)
        self.cursor = QCursor(pix)
        self.setCursor(self.cursor)     # le curseur en forme de cible
        self.pos_zoom = vecteur(50, 50) # point initialement grossi dans le zoom
        self.image_w = self.width()     # deux valeurs par défaut
        self.image_h = self.height()    # pas forcément pertinentes
        self.setMouseTracking(True)
        self.origine = vecteur(self.width()//2, self.height()//2)
        self.echelle_image = echelle()  # objet gérant l'échelle
        self.decal = vecteur(0, 0)      # if video is not 4:3, center video
        self.couleurs = [
            "red", "blue", "cyan", "magenta", "yellow", "gray", "green"] *2
        self.tourne = False        # au cas où on fait tourner les images
        self.premier_resize = True # devient faux après redimensionnement
        self.rotation = False      # permet de retourner une vidéo mal prise
        self.image_max = None      # numéro de la dernière image de la vidéo
        self.framerate = None      # nombre d'images par seconde
        # dimensions natives des images de la vidéo
        self.largeurFilm, self.hauteurFilm = None, None
        self.index = None          # index de l'image courante
        self.objet_courant = 1     # désignation de l'objet courant
        self.a_une_image = False   # indication quant à une image disponible
        self.imageExtraite = None  # référence de l'image courante
        self.origine = None        # position de l'origine sur les images
        self.lance_capture = False # un pointage est en cours
        self.decal = vecteur(0,0)  # décalage des images
        self.echelle_faite = False # vrai quand l'échelle est définie
        self.modifie = False       # permet de suivre les pointages manuels
        self.echelle_trace = None  # widget pour tracer l'échelle
        self.selRect = None        # un objet gérant la sélection par rectangle
        self.lance_cature = False  # devient vrai quand on commence à pointer
        self.auto = False          # devient vrai pour le pointage automatique
        self.sens_X = 1            # sens de l'axe des abscisses
        self.sens_Y = 1            # sens de l'axe des ordonnées
        self.motifs_auto = []      # liste de motifs pour le suivi auto
        self.pointsProbables = {}  # dictionnaire de points proches de la détection ?

        # connexion des signaux
        self.clic_sur_video_signal.connect(self.clic_sur_la_video)
        self.selection_motif_done.connect(self.suiviDuMotif)
        self.stopCalculs.connect(self.stopComputing)

        return

    # signaux de la classe
    clic_sur_video_signal = pyqtSignal()
    selection_motif_done = pyqtSignal()
    stopCalculs = pyqtSignal()

    def setApp(self, app):
        """
        Connecte le videoWidget à sa fenêtre principale, et connecte
        aussi les sous-widgets nécessaires, ceux que le videoWidget doit
        pouvoir contrôler
        """
        self.app = app
        # réplication de certains attributs de la fenêtre principale
        attributes = [
            "dbg", "horizontalSlider",
            "spinBox_image", "spinBox_nb_de_points", "spinBox_chrono",
            "Bouton_lance_capture", "Bouton_Echelle", "tabWidget",
            "graphWidget", "tableWidget", "tab_traj", "comboBox_referentiel",
            "pushButton_select_all_table", "pushButton_origine",
            "checkBox_abscisses", "checkBox_ordonnees", "checkBox_auto",
            "Bouton_lance_capture", "pushButton_rot_droite",
            "pushButton_rot_gauche", "pushButton_defait", "pushButton_refait",
            "pushButton_stopCalculs", "checkBox_Ec", "checkBox_Em",
            "checkBox_Epp", "checkBoxScale",
        ]
        for a in attributes:
            setattr(self, a, getattr(app,a))
        # connexion de signaux de widgets
        self.spinBox_nb_de_points.valueChanged.connect(self.redimensionne_data)
        return
    
    def redimensionne_data(self):
        """
        redimensionne self.data (fonction de rappel connectée aux
        changements de self.spinBox_nb_de_points
        """
        if self.image_max and self.deltaT:
            self.dimensionne(
                self.spinBox_nb_de_points.value(), self.deltaT, self.image_max)
            self.app.cree_tableau(nb_obj = self.nb_obj)
        return

    @property
    def nb_obj(self):
        """
        @return le nombre d'objets suivis
        """
        return len(self.suivis)
    
    def setZoom(self, zoom):
        self.zoom = zoom
        return
    
    def clear(self):
        self.image = None
        return

    def updateZoom(self, position = None):
        """
        place dans le widget de zoom une image agrandie pertinente
        @param position l'endroit où prendre l'image à agrandir ; si
          position == None (par défaut) ça signifie vecteur(50,50)
        """
        if position is None :
            position = vecteur(50,50)
        self.zoom.fait_crop(self.image, position)
        return
    
    def cache_zoom(self):
        return

    def placeImage(self, im, ratio):
        """
        place une image dans le widget, en conservant le ratio de cette image
        @param im une image
        @param ratio le ratio à respecter
        @return l'image, redimensionnée selon le ratio
        """
        self.image_w = min(self.width(), round(self.height() * ratio))
        self.image_h = round(self.image_w / ratio)
        self.setMouseTracking(True)
        image = im.scaled(self.image_w, self.image_h)
        self.app.imageAffichee = image # verrue nécessaire avant met_a_jour_crop
        self.setImage(image)
        self.updateZoom()
        self.reinit_origine()
        return image
    
    def reinit_origine(self):
        """
        Replace l'origine au centre de l'image
        """
        self.origine = vecteur(self.image_w//2, self.image_h//2)
        return

    def reinit(self):
        self.updateZoom()
        self.setMouseTracking(True)
        self.update()
        self.setCursor(Qt.ArrowCursor)
        self.setEnabled(1)
        self.reinit_origine()
        self.pointsProbables = {}
        self.motifs_auto = []
        self.redimensionne_data()
        return

    def maj(self, tourne=False):
        if tourne:
            self.tourne = True
        return

    def resizeEvent(self, e):
        if self.premier_resize:  # Au premier resize, la taille est changée mais pas l'origine.
            self.premier_resize = False
            self.reinit_origine()

        if e.oldSize() != QSize(-1, -1):
            if not self.app.tourne:
                ratiow = self.width()/e.oldSize().width()
                ratioh = self.height()/e.oldSize().height()
            else:
                ratiow = self.width()/e.oldSize().height()
                ratioh = self.height()/e.oldSize().width()
            x = self.origine.x*ratiow
            y = self.origine.y*ratioh
            if not self.app.premier_chargement_fichier_mecavideo:
                self.origine = vecteur(x, y)


            if self.echelle_faite:
                x = self.echelle_image.p1.x*ratiow
                y = self.echelle_image.p1.y*ratioh
                self.echelle_image.p1 = vecteur(x, y)

                x = self.echelle_image.p2.x*ratiow
                y = self.echelle_image.p2.y*ratioh
                self.echelle_image.p2 = vecteur(x, y)
                
                self.feedbackEchelle(
                    self.echelle_image.p1, self.echelle_image.p2)
        return

    def storePoint(self, point):
        """
        enregistre un point, quand self.index et self.objet_courant
        sont déjà bien réglés.
        @param point la position à enregistrer
        """
        if self.lance_capture == True:
            self.pointe(self.objet_courant, point, index=self.index-1)
            self.clic_sur_video_signal.emit()
            self.updateZoom(self.hotspot)
            self.update()
        return

    def mouseReleaseEvent(self, event):
        if self.lance_capture == True:
            self.pointe(self.objet_courant, event, index=self.index-1)
            self.objetSuivant()
            self.clic_sur_video_signal.emit()
            self.updateZoom(self.hotspot)
            self.update()
        return

    def objetSuivant(self):
        """
        passage à l'objet suivant pour le pointage.
        revient au premier objet quand on a fait le dernier, et
        change d'image aussi
        """
        i = self.suivis.index(self.objet_courant)
        if i < self.nb_obj - 1 :
            self.objet_courant = self.suivis[i+1]
        else:
            # on passe à l'image suivante, et on revient au premier objet
            self.objet_courant = self.suivis[0]
            if self.index < self.image_max:
                self.index +=1
        return

    def enterEvent(self, event):
        if self.lance_capture == True and self.auto == False:
            # beau curseur seulment si la capture manuelle est lancée
            beauGrosCurseur(self)
        else:
            self.setCursor(Qt.ArrowCursor)
        return
    
    def mouseMoveEvent(self, event):
        if self.lance_capture == True and self.auto == False:
            # ne se lance que si la capture manuelle est lancée
            self.hotspot = vecteur(event.x(), event.y())
            self.updateZoom(self.hotspot)
        return
    
    def paintEvent(self, event):
        if self.image:
            if self.echelle_faite and self.lance_capture:
                self.updateZoom(self.hotspot)

            painter = QPainter()
            painter.begin(self)
            if self.image != None:
                painter.drawPixmap(
                    round(self.decal.x), round(self.decal.y), self.image)

            ############################################################
            # dessin de l'origine
            longueur_origine = 5
            painter.setPen(Qt.green)
            painter.drawLine(
                round(self.origine.x) - longueur_origine, round(self.origine.y),
                round(self.origine.x) + longueur_origine, round(self.origine.y))
            painter.drawLine(
                round(self.origine.x), round(self.origine.y) - longueur_origine,
                round(self.origine.x), round(self.origine.y) + longueur_origine)
            painter.drawText(
                round(self.origine.x), round(self.origine.y) + 15, "O")
            ############################################################
            # draw points
            self.dbg.p(
                5, "In videoWidget, paintEvent, self.data :%s" % self.data)
            if self.data:
                for date in self.data:
                    for obj in self.data[date]:
                        point = self.data[date][obj]
                        if point:
                            painter.setPen(QColor(self.couleurs[int(obj)-1]))
                            painter.setFont(QFont("", 10))
                            painter.translate(point.x, point.y)
                            painter.drawLine(-2, 0, 2, 0)
                            painter.drawLine(0, -2, 0, 2)
                            painter.translate(-10, +10)
                            painter.drawText(0, 0, str(obj))
                            painter.translate(-point.x + 10, -point.y - 10)

            ############################################################
            # paint repere
            painter.setPen(Qt.green)
            painter.translate(0, 0)
            try:
                painter.translate(
                    round(self.origine.x), round(self.origine.y))
            except AttributeError:
                pass
            p1 = QPoint(round(self.sens_X * (-40)), 0)
            p2 = QPoint(round(self.sens_X * (40)), 0)
            p3 = QPoint(round(self.sens_X * (36)), 2)
            p4 = QPoint(round(self.sens_X * (36)), -2)
            painter.scale(1, 1)
            painter.drawPolyline(p1, p2, p3, p4, p2)
            painter.rotate(self.sens_X * self.sens_Y * (-90))
            painter.drawPolyline(p1, p2, p3, p4, p2)
            ############################################################

            painter.end()
        return

    def extract_image(self, index):
        """
        extrait une image de la video à l'aide d'OpenCV
        @param index le numéro de l'image (commence à 1)

        @return un boolen (ok), et l'image au format d'openCV ; l'image
          au bon format pour Qt est dans self.imageExtraite
        """
        self.dbg.p(1, "rentre dans 'extract_image' " + 'index : ' + str(index))
        ok, image_opencv = self.cvReader.getImage(index, self.rotation)
        if not ok:
            self.affiche_barre_statut(
                _translate("pymecavideo", "Pymecavideo n'arrive pas à lire l'image", None))
            return False, None
        self.a_une_image = ok
        self.imageExtraite = toQImage(image_opencv)
        return ok, image_opencv

    def calcul_deltaT(self, ips_from_line_edit=False, rouvre=False):
        """
        Détermination de l'intervalle de temps entre deux images.
        Cela modifie self.deltaT

        @param ips_from_line_edit (faux par défaut) indique qu'on lit 
         deltaT depuis un champ de saisie
        @param rouvre (faux par défaut) indique qu'on lit les données depuis
         un fichier pymecavidéo
        """
        self.dbg.p(1, "rentre dans 'calcul_deltaT'")
        if rouvre:
            # se produit quand on lit un deltaT depuis un fichier mecavideo
            IPS = round(1/self.deltaT)
            self.app.lineEdit_IPS.setText(str(IPS))
        else:
            if not ips_from_line_edit:
                self.deltaT = 1 / self.framerate
                # mets à jour le widget contenant les IPS
                self.app.lineEdit_IPS.setText(str(self.framerate))
            else:
                IPS = int(self.app.lineEdit_IPS.text())
                self.framerate = IPS
                self.deltaT = 1 / IPS
        return
    
    def active_controle_image(self, state=True):
        """
        Gère les deux widgets horizontalSlider et spinBox_image
        @param state (vrai par défaut) ; si state == True, les deux
          widgets sont activés et leurs signaux valueChanged sont pris
          en compte ; sinon ils sont désactivés ainsi que les signaux
        """
        if state:
            self.horizontalSlider.setMinimum(1)
            self.spinBox_image.setMinimum(1)
            if self.image_max:
                self.horizontalSlider.setMaximum(int(self.image_max))
                self.spinBox_image.setMaximum(int(self.image_max))
            self.horizontalSlider.valueChanged.connect(
                self.app.affiche_image_slider_move)
            self.spinBox_image.valueChanged.connect(self.affiche_image_spinbox)
        else:
            if self.horizontalSlider.receivers(self.horizontalSlider.valueChanged):
                self.horizontalSlider.valueChanged.disconnect()
            if self.spinBox_image.receivers(self.spinBox_image.valueChanged):
                self.spinBox_image.valueChanged.disconnect()
        self.horizontalSlider.setEnabled(state)
        self.spinBox_image.setEnabled(state)
        return
        
    def affiche_echelle(self):
        """
        affiche l'échelle courante pour les distances sur l'image
        """
        self.dbg.p(1, "rentre dans 'affiche_echelle'")
        if self.echelle_image.isUndef():
            self.app.echelleEdit.setText(
                _translate("pymecavideo", "indéf.", None))
            self.app.Bouton_Echelle.setEnabled(True)
        else:
            epxParM = self.echelle_image.pxParM()
            if epxParM > 20:
                self.app.echelleEdit.setText("%.1f" % epxParM)
            else:
                self.app.echelleEdit.setText("%8e" % epxParM)
        self.app.echelleEdit.show()
        self.app.Bouton_Echelle.show()
        return

    def init_image(self):
        """
        initialise certaines variables lors le la mise en place d'une 
        nouvelle vidéo
        """
        self.dbg.p(1, "rentre dans 'init_image'")
        self.index = 1
        self.extract_image(1)
        self.framerate, self.image_max, self.largeurFilm, self.hauteurFilm = \
            self.cvReader.recupere_avi_infos(self.rotation)
        self.ratio = self.largeurFilm / self.hauteurFilm
        self.app.init_interface()
        self.trajectoire = {}
        self.calcul_deltaT()
        # on dimensionne les données pour les pointages
        self.redimensionne_data()
        self.active_controle_image()
        self.echelle_image = echelle()
        self.affiche_echelle()
        self.affiche_image()
        return

    def affiche_image(self):
        self.dbg.p(1, "rentre dans 'affiche_image'" + ' ' +
                   str(self.index) + ' ' + str(self.image_max))
        if not self.filename:
            return
        if self.index <= self.image_max:
            self.extract_image(self.index)  # 2ms
            self.afficheJusteImage()  # 4 ms
            if self.horizontalSlider.value() != self.index:
                self.dbg.p(1, "affiche_image " + "horizontal")
                i = int(self.index)
                self.horizontalSlider.setValue(i)
                self.spinBox_image.setValue(i)  # 0.01 ms
        elif self.index > self.image_max:
            self.index = self.image_max
            self.lance_capture = False
        return
    
    def afficheJusteImage(self):
        if self.a_une_image:
            self.placeImage(self.imageExtraite, self.ratio)
        return
    
    def init_cvReader(self):
        """
        Initialise le lecteur de flux vidéo pour OpenCV
        et recode la vidéo si nécessaire.
        """
        self.dbg.p(1, "rentre dans 'init_cvReader', ouverture de %s" %
                   (self.filename))
        self.cvReader = openCvReader(self.filename)
        time.sleep(0.1)
        if not self.cvReader.ok:
            QMessageBox.warning(None, "Format vidéo non pris en charge",
                                _translate("pymecavideo", """\le format de cette vidéo n'est pas pris en charge par pymecavideo""",
                                           None),
                                QMessageBox.Ok, QMessageBox.Ok)
        else:
            return True

    def init_capture(self):
        """
        Prépare une session de pointage, au niveau de la
        fenêtre principale, et met à jour les préférences
        """
        self.app.prefs.lastVideo = self.filename
        self.app.prefs.videoDir = os.path.dirname(self.filename)
        self.app.prefs.save()

        self.spinBox_image.setMinimum(1)
        self.spinBox_chrono.setMaximum(self.image_max)
        self.spinBox_nb_de_points.setEnabled(True)
        self.tab_traj.setEnabled(0)
        self.tabWidget.setTabEnabled(0, True)
        self.active_controle_image()
        self.app.actionCopier_dans_le_presse_papier.setEnabled(1)
        self.app.menuE_xporter_vers.setEnabled(1)
        self.app.actionSaveData.setEnabled(1)

        self.app.affiche_barre_statut(
            _translate("pymecavideo", "Veuillez choisir une image (et définir l'échelle)", None))
        self.Bouton_Echelle.setEnabled(True)
        self.active_controle_image()
        self.checkBox_abscisses.setEnabled(1)
        self.checkBox_ordonnees.setEnabled(1)
        self.checkBox_auto.setEnabled(1)
        self.Bouton_lance_capture.setEnabled(True)
        self.app.montre_vitesses = False
        try:
            self.app.trajectoire_widget.update()  # premier lancement sans fichier
        except AttributeError as err:
            self.dbg.p(3, f"***Exception*** {err} at line {get_linenumber()}")
            pass
        return

    def openTheFile(self, filename):
        """
        Ouvre le fichier de nom filename, enregistre les préférences de
        fichier vidéo.
        @param filename nom du fichier
        """
        self.dbg.p(1, "rentre dans 'openTheFile'")
        if not filename :
            return
        self.filename = filename
        goOn = self.init_cvReader()
        if goOn:  # le fichier vidéo est OK, et son format est reconnu
            self.init_image()
            self.init_capture()
            self.change_axe_ou_origine()
        else:
            QMessageBox.warning(
                None,
                _translate("pymecavideo", "Erreur lors de la lecture du fichier", None),
                _translate("pymecavideo", "Le fichier<b>{0}</b> ...\nn'est peut-être pas dans un format vidéo supporté.", None).format(
                    filename),
                QMessageBox.Ok, QMessageBox.Ok)
        return
    
    def change_axe_ou_origine(self, origine=None):
        """mets à jour le tableau de données"""
        self.dbg.p(1, "rentre dans 'change_axe_ou_origine'")
        self.dbg.p(3, "valeur de l'origine en argument %s"%(origine))
        # repaint axes and define origine
        if origine is not None:
            self.origine = origine
        self.app.trajectoire_widget.origine_mvt = self.origine
        self.app.trajectoire_widget.update()
        self.update()
        return
    
    def affiche_point_attendu(self, obj):
        """
        Renseigne sur le numéro d'objet du point attendu
        affecte la ligne de statut et la ligne sous le zoom
        @param obj l'objet courant
        """
        self.app.affiche_barre_statut(
            _translate("pymecavideo", "Pointage des positions : cliquer sur le point N° {0}", None).format(obj))
        return

    def clic_sur_la_video(self, liste_points=None, interactif=True):
        self.dbg.p(1, "rentre dans 'clic_sur_video'")
        self.lance_capture = True
        if self.index <= self.image_max:
            # si on n'atteint pas encore la fin de la vidéo
            self.purge_refaire() # oublie les pointages à refaire
            if interactif:
                self.modifie = True
            self.clic_sur_video_ajuste_ui(self.objet_courant)
        if self.index > self.image_max:
            self.lance_capture = False
            self.affiche_barre_statut(_translate(
                "pymecavideo", "Vous avez atteint la fin de la vidéo", None))
            self.index = self.image_max
        self.app.recalculLesCoordonnees()
        return
    
    def clic_sur_video_ajuste_ui(self, objet_courant):
        """
        Ajuste l'interface utilisateur pour attendre un nouveau clic
        @param point_attendu le numéro du point qui est à cliquer
        """
        self.dbg.p(1, "rentre dans 'clic_sur_video_ajuste_ui'")
        self.affiche_image()
        self.affiche_point_attendu(self.objet_courant)
        self.enableDefaire(self.peut_defaire())
        self.enableRefaire(self.peut_refaire())
        return

    def affiche_nb_points(self, active=False):
        """
        Met à jour l'afficheur de nombre de points à saisir
        @param active vrai si on doit permettre la saisie du nombre de points
        """
        self.dbg.p(1, "rentre dans 'affiche_nb_points'")
        self.spinBox_nb_de_points.setEnabled(active)
        if self.data:
            self.spinBox_nb_de_points.setValue(self.nb_obj)
        return


    def affiche_lance_capture(self, active=False):
        """
        Met à jour l'affichage du bouton pour lancer la capture
        @param active vrai si le bouton doit être activé
        """
        self.Bouton_lance_capture.setEnabled(active)
        return

    def debut_capture(self, departManuel=True, rouvre=False):
        """
        permet de mettre en place le nombre de point à acquérir
        @param departManuel vrai si on a fixé à la main la première image.
        @param rouvre  : ne mets pas à jour self.premiere_image_pointee 
          à partir du slider.
        """
        self.dbg.p(1, "rentre dans 'debut_capture'")
        self.setFocus()
        self.show()
        self.activateWindow()
        self.setVisible(True)
        # nécessaire sinon, video n'est pas actif.
        if self.echelle_trace: self.echelle_trace.lower()
        self.affiche_lance_capture(False)
        self.active_controle_image(False)
        self.tabWidget.setEnabled(1)
        self.tabWidget.setTabEnabled(3, True)
        self.tabWidget.setTabEnabled(2, True)
        self.tabWidget.setTabEnabled(1, True)
        self.arretAuto = False
        if not rouvre :
            # si rouvre, self.premiere_image_pointee est déjà définie
            self.premiere_image_pointee = self.horizontalSlider.value()
        self.affiche_point_attendu(1)
        self.lance_capture = True
        self.app.fixeLesDimensions()
        self.setCursor(Qt.CrossCursor)
        self.tab_traj.setEnabled(1)
        self.app.actionSaveData.setEnabled(1)
        self.app.actionCopier_dans_le_presse_papier.setEnabled(1)
        self.comboBox_referentiel.setEnabled(1)
        self.pushButton_select_all_table.setEnabled(1)

        self.comboBox_referentiel.clear()
        self.comboBox_referentiel.insertItem(-1, "camera")
        for obj in self.suivis:
            self.comboBox_referentiel.insertItem(-1, _translate(
                "pymecavideo", "point N° {0}", None).format(str(obj)))

        self.pushButton_origine.setEnabled(0)
        self.checkBox_abscisses.setEnabled(0)
        self.checkBox_ordonnees.setEnabled(0)
        self.checkBox_auto.setEnabled(0)
        # self.Bouton_Echelle.setEnabled(0)
        self.Bouton_lance_capture.setEnabled(0)
        self.pushButton_rot_droite.setEnabled(0)
        self.pushButton_rot_gauche.setEnabled(0)

        # on empêche le redimensionnement
        self.app.fixeLesDimensions()

        # si aucune échelle n'a été définie, on place l'étalon à 1 px pou 1 m.
        if self.echelle_image.mParPx() == 1:
            self.echelle_image.longueur_reelle_etalon = 1
            self.echelle_image.p1 = vecteur(0, 0)
            self.echelle_image.p1 = vecteur(0, 1)

        # automatic capture
        if self.checkBox_auto.isChecked():
            #self.auto = True
            self.app.affiche_barre_statut(
                _translate("pymecavideo", "Pointage Automatique", None))
            reponse = QMessageBox.warning(None, "Capture Automatique",
                                          _translate("pymecavideo", """\
Veuillez sélectionner un cadre autour du ou des objets que vous voulez suivre.
Vous pouvez arrêter à tout moment la capture en appuyant sur le bouton STOP""",
                                                     None),
                                          QMessageBox.Ok, QMessageBox.Ok)
            if self.selRect:
                self.selRect.finish(delete=True)
            # in this widget, motif(s) are defined.
            self.selRect = SelRectWidget(self)
            self.selRect.show()
            # IMPORTANT : permet de gagner en fluidité de l'affichage
            # lors du pointage automatique.
            self.active_controle_image(False)
        return

    def feedbackEchelle(self, p1, p2):
        """
        affiche une trace au-dessus du self.job, qui reflète les positions
        retenues pour l'échelle
        """
        self.dbg.p(1, "rentre dans 'feedbackEchelle'")
        if self.echelle_trace:
            self.echelle_trace.hide()

        self.echelle_trace = Echelle_TraceWidget(self, p1, p2)
        # on garde les valeurs pour le redimensionnement
        self.echelle_trace.show()
        if self.echelle_faite:
            self.mets_en_orange_echelle()
            self.Bouton_Echelle.setEnabled(1)
        return

    def reinitialise_capture(self):
        """
        Efface toutes les données de la capture en cours et prépare une nouvelle
        session de capture.
        """
        self.dbg.p(1, "rentre dans 'reinitialise_capture'")

        # ferme les widget d'affichages des x, y, v du 2e onglets si elles existent
        for plotwidget in self.app.dictionnairePlotWidget.values():
            plotwidget.parentWidget().close()
            plotwidget.close()
            del plotwidget

        self.rotation = False
        self.app.defixeLesDimensions()
        self.reinit()
        if self.echelle_trace:
            self.echelle_trace.hide()
        self.Bouton_Echelle.setText(_translate(
            "pymecavideo", "Définir l'échelle", None))
        self.Bouton_Echelle.setStyleSheet("background-color:None;")
        self.app.init_variables(tuple(), filename=self.filename)
        self.affiche_image()
        self.echelle_image = echelle()
        self.affiche_echelle()
        self.active_controle_image()
        self.spinBox_image.setValue(1)
        self.enableDefaire(False)
        self.enableRefaire(False)
        self.affiche_nb_points(1)
        self.Bouton_lance_capture.setEnabled(1)

        # désactive le bouton de calculs si existant :
        self.pushButton_stopCalculs.setEnabled(0)
        self.pushButton_stopCalculs.hide()

        # désactive graphe si existant
        if self.graphWidget:
            plotItem = self.graphWidget.getPlotItem()
            plotItem.clear()
            plotItem.setTitle('')
            plotItem.hideAxis('bottom')
            plotItem.hideAxis('left')
        ### Réactiver checkBox_avancees après réinitialisation ###
        self.pushButton_origine.setEnabled(1)
        self.checkBox_abscisses.setEnabled(1)
        self.checkBox_ordonnees.setEnabled(1)
        self.checkBox_auto.setEnabled(1)
        self.checkBox_abscisses.setCheckState(Qt.Unchecked)
        self.checkBox_ordonnees.setCheckState(Qt.Unchecked)
        self.checkBox_auto.setCheckState(Qt.Unchecked)
        if self.a_une_image:
            self.pushButton_rot_droite.setEnabled(1)
            self.pushButton_rot_gauche.setEnabled(1)
        else:
            self.pushButton_rot_droite.setEnabled(0)
            self.pushButton_rot_gauche.setEnabled(0)
        # réactive les contrôles de l'image (spinbox et slider) :
        self.active_controle_image()
        self.tabWidget.setTabEnabled(3, False)
        self.tabWidget.setTabEnabled(2, False)
        self.tabWidget.setTabEnabled(1, False)
        self.checkBox_Ec.setChecked(0)
        self.checkBox_Em.setChecked(0)
        self.checkBox_Epp.setChecked(0)

        # HACK : oblige le redimensionnement
        self.resize(self.size()+QSize(1, 0))
        self.resize(self.size()+QSize(-1, 0))
        return
    
    def enableDefaire(self, value):
        """
        Contrôle la possibilité de défaire un clic
        @param value booléen
        """
        self.dbg.p(1, "rentre dans 'enableDefaire, %s'" % (str(value)))
        self.pushButton_defait.setEnabled(value)
        self.app.actionDefaire.setEnabled(value)
        # permet de remettre l'interface à zéro
        if not value:
            self.active_controle_image()
        return
    
    def enableRefaire(self, value):
        """
        Contrôle la possibilité de refaire un clic
        @param value booléen
        """
        self.dbg.p(1, "rentre dans 'enableRefaire, %s'" % (value))
        self.pushButton_refait.setEnabled(value)
        self.app.actionRefaire.setEnabled(value)

    def demande_echelle(self):
        """
        demande l'échelle interactivement
        """
        self.dbg.p(1, "rentre dans 'demande_echelle'")
        reponse, ok = QInputDialog.getText(
            None,
            _translate("pymecavideo", "Définir léchelle", None),
            _translate("pymecavideo", "Quelle est la longueur en mètre de votre étalon sur l'image ?", None),
            QLineEdit.Normal,
            f"{self.echelle_image.longueur_reelle_etalon:.3f}")
        if not ok:
            return
        try:
            reponse = float(reponse.replace(",", "."))
            if reponse <= 0:
                self.app.affiche_barre_statut(_translate(
                    "pymecavideo", " Merci d'indiquer une échelle valable", None))
            else:
                self.echelle_image.etalonneReel(reponse)
                self.job = EchelleWidget(self, self.app)
                self.job.show()
                self.change_axe_ou_origine()
        except ValueError as err:
            self.affiche_barre_statut(_translate(
                "pymecavideo", " Merci d'indiquer une échelle valable", None))
            self.demande_echelle()
        return
    
    def mets_en_orange_echelle(self):
        self.Bouton_Echelle.setEnabled(1)
        self.Bouton_Echelle.setText("refaire l'échelle")
        self.Bouton_Echelle.setStyleSheet("background-color:orange;")
        return

    def rouvre(self, fichier):
        """
        Rouvre un fichier pymecavideo précédemment enregistré
        """
        self.dbg.p(1, "rentre dans 'rouvre'")
        self.reinitialise_capture()
        lignes = open(fichier, "r").readlines()

        # réinitialisation des données de pointage
        self.data    = None
        self.suivis  = None
        self.deltaT  = None
        self.echelle = None
        self.vide    = True

        self.echelle_image = echelle()  # on réinitialise l'échelle
        # on récupère les données importantes
        dico_donnees = self.load_lignes_donnees(lignes)
        self.check_uncheck_direction_axes()  # check or uncheck axes Checkboxes
        self.app.init_interface()
        self.change_axe_ou_origine()

        # puis on trace le segment entre les points cliqués pour l'échelle
        # on réinitialise l'échelle.p1, self.echelle_image.p2)
        self.feedbackEchelle(
            self.echelle_image.p1, self.echelle_image.p2)
        self.framerate, self.image_max, self.largeurFilm, self.hauteurFilm = self.cvReader.recupere_avi_infos(
            self.rotation)
        self.ratio = self.largeurFilm / self.hauteurFilm
        self.rouvert = True
        self.premierResize = False



        # on régénère self.data
        index = -1
        for l in lignes:
            if not l.strip() or l[0] == "#":
                # on ne s'occupe ni des commentaires ni des lignes vides
                pass
            else:
                index += 1
                l = l.strip('\t\n')
                d = l.split("\t")
                n_suivis = (len(d) - 1) // 2
                if not self.data:
                    self.dimensionne(n_suivis, self.deltaT, self.image_max)
                t = float(d[0].replace(",", "."))
                obj = 1
                for j in range(1, len(d), 2):
                    x = self.origine.x + self.sens_X * round(float(
                        d[j].replace(",", ".")) * self.echelle_image.pxParM())
                    y = self.origine.y - self.sens_Y * round((float(
                        d[j + 1].replace(",", ".")) * self.echelle_image.pxParM()))
                    pos = vecteur(x,y)
                    self.pointe(obj, pos, index = \
                                index + self.premiere_image_pointee - 1)
                    obj += 1
        self.active_controle_image()
        self.extract_image(1)
        self.affiche_echelle()  # on met à jour le widget d'échelle
        self.horizontalSlider.setValue(self.image_max)
        self.spinBox_image.setValue(self.image_max)
        self.spinBox_chrono.setMaximum(self.image_max)
        self.enableDefaire(False)
        self.enableRefaire(False)
        self.affiche_image()  # on affiche l'image
        self.mets_en_orange_echelle()
        self.tableWidget.show()
        self.app.recalculLesCoordonnees()
        ##HACK oblige le redimensionnement pour mettre à jour l'image
        self.resize(self.size()+QSize(1, 0))
        self.resize(self.size()+QSize(-1, 0))
        self.debut_capture(rouvre=True)

        return
    
    def load_lignes_donnees(self, lignes):
        """
        Lit les lignes du fichier pymecavidéo de type commentaire
        pour en déduire un dictionnaire de protpriéts utiles
        Rappel : la structure de l'en-tête du fichier est
#pymecavideo
#video = {self.filename}
#sens axe des X = {self.sens_X}
#sens axe des Y = {self.sens_Y}
#largeur video = {self.width()}
#hauteur video = {self.height()}
#rotation = {self.rotation}
#origine de pointage = {self.origine}
#index de depart = {self.premiere_image_pointee}
#echelle {self.echelle_image.longueur_reelle_etalon} m pour {self.echelle_image.longueur_pixel_etalon()} pixel
#echelle pointee en {self.echelle_image.p1 if self.echelle_faite else None} {self.echelle_image.p2 if self.echelle_faite else None}
#intervalle de temps : {self.deltaT}
#suivi de {self.nb_obj} point(s)
#{msg}
#        """
        self.dbg.p(1, "rentre dans 'load_lignes_donnees'")
        en_tete = [l for l in lignes if l[0] == "#"]
        dico_donnee={}
        for l in en_tete:
            if re.match("#echelle pointee en .*", l):
                self.echelle_faite = l.split()[-1]!='None'
                if self.echelle_faite:
                    x1 = float(l.split()[3][1:-1])
                    y1 = float(l.split()[4][:-1])
                    self.echelle_image.p1 = vecteur(x1, y1)
                    x2 = float(l.split()[5][1:-1])
                    y2 = float(l.split()[6][:-1])
                    self.echelle_image.p2 = vecteur(x2, y2)
            m = re.match("#echelle (.*) m pour .* pixel.*", l)
            if m:
                self.echelle_image.longueur_reelle_etalon = float(m.group(1))
            m = re.match("#(.*) = (.*)", l)
            if m:
                dico_donnee[m.group(1)] = m.group(2).strip()
            m = re.match("#intervalle de temps : (.*)", l)
            if m:
                self.deltaT = float(m.group(1))
            m = re.match("#suivi de (.*) point.*", l)
            if m:
                nb_suivis = int(m.group(1))
                
        self.filename = dico_donnee["video"]
        self.sens_X = int(dico_donnee['sens axe des X'])
        self.sens_Y = int(dico_donnee['sens axe des Y'])
        largeur = int(dico_donnee['largeur video'])
        hauteur = int(dico_donnee['hauteur video'])
        self.rotation = dico_donnee['rotation'] in ("1", "True")
        self.origine = vecteur(
            dico_donnee['origine de pointage'].split()[-2][1:-1],
            dico_donnee['origine de pointage'].split()[-1][:-1]
        )
        self.premier_chargement_fichier_mecavideo = True
        self.premiere_image_pointee = int(dico_donnee['index de depart'])

        self.calcul_deltaT(rouvre=True)
        self.init_cvReader()
        self.framerate, self.image_max, self.largeurFilm, self.hauteurFilm = \
            self.cvReader.recupere_avi_infos(self.rotation)
        self.suivis = list(range(1, nb_suivis+1))
        self.spinBox_nb_de_points.setValue(nb_suivis)
        self.redimensionne_data()
        self.resize(QSize(largeur, hauteur))
        ########redimensionne l'application TODO : ATTENTION
        decalage_gauche = 220
        decalage_haut = 130
        self.app.setGeometry(self.pos().x(),self.pos().y()+37, self.width()+decalage_gauche, self.height()+decalage_haut)

        return dico_donnee

    def check_uncheck_direction_axes(self):
        """
        met à jour les axes selon les sens connus
        """
        if self.sens_X == -1:
            self.checkBox_abscisses.setChecked(1)
        else:
            self.checkBox_abscisses.setChecked(0)
        if self.sens_Y == -1:
            self.checkBox_ordonnees.setChecked(1)
        else:
            self.checkBox_ordonnees.setChecked(0)
        return

    def suiviDuMotif(self):
        self.dbg.p(1, "rentre dans 'suiviDuMotif'")
        if len(self.motifs_auto) == self.nb_obj:
            self.dbg.p(3, "selection des motifs finie")
            self.selRect.finish(delete=True)
            self.indexMotif = 0
            self.pushButton_stopCalculs.setText("STOP")
            self.pushButton_stopCalculs.setEnabled(1)
            self.pushButton_stopCalculs.show()
            self.setEnabled(0)
            self.pileDeDetections = []
            for i in range(self.index, self.image_max+1):
                for j in range(self.nb_obj):
                    self.pileDeDetections.append(i)
            # programme le suivi du point suivant après un délai de 50 ms,
            # pour laisser une chance aux évènement de l'interface graphique
            # d'être traités en priorité
            self.dbg.p(3, "self.pileDeDetections : %s" % self.pileDeDetections)
            timer = QTimer.singleShot(50, self.detecteUnPoint)

    # @time_it
    def detecteUnPoint(self):
        """
        méthode (re)lancée pour les détections automatiques de points
        traite une à une les données empilées dans self.pileDeDetections
        et relance un signal si la pile n'est pas vide après chacun
        des traitements.
        """
        self.dbg.p(1, "rentre dans 'detecteUnPoint'")
        if self.pileDeDetections:
            # on dépile un index de détections à faire et on met à jour
            # le bouton de STOP
            self.pushButton_stopCalculs.setText(
                f"STOP ({self.pileDeDetections.pop(0)})")
            ok, image = self.cvReader.getImage(
                self.index, self.rotation, rgb=False)
            # puis on boucle sur les objets à suivre et on
            # détecte leurs positions
            # Ça pourrait bien se faire dans des threads, en parallèle !!!
            for i in range(self.nb_obj):
                self.indexMotif = i
                part = self.motifs_auto[self.indexMotif]
                zone_proche = self.pointsProbables.get(self.objet_courant, None)
                echelle = self.image_w / self.largeurFilm
                point = filter_picture(part, image, echelle, zone_proche)
                self.pointsProbables[self.objet_courant] = point
                self.storePoint(vecteur(point[0], point[1]))
                # le point étant détecté, on passe à l'objet suivant
                # et si nécessaire à l'image suivante
                self.objetSuivant()
            # le numéro d'image ayant changé, on la récupère à nouveau.
            self.extract_image

            # programme le suivi du point suivant après un délai de 50 ms,
            # pour laisser une chance aux évènement de l'interface graphique
            # d'être traités en priorité
            timer = QTimer.singleShot(50, self.detecteUnPoint)
        else:
            self.stopCalculs.emit()

    def storeMotif(self):
        self.dbg.p(1, "rentre dans 'storeMotif'")
        if len(self.motifs_auto) == self.nb_obj:
            self.dbg.p(3, "selection des motifs finie")
            self.selRect.finish()
            self.indexMotif = 0
            self.pushButton_stopCalculs.setText("STOP")
            self.pushButton_stopCalculs.setEnabled(1)
            self.pushButton_stopCalculs.show()
            self.setEnabled(0)
            self.goCalcul = True
            # TODO : tests avec les différents mode de threading
            if self.methode_thread == 1:
                self.monThread = MonThreadDeCalcul(
                    self, self.motifs_auto[self.indexMotif], self.imageAffichee)
                self.monThread.start()
            elif self.methode_thread == 2:  # 1 thread par image
                for i in range((self.image_max-self.premiere_image_pointee)*self.nb_obj):
                    self.liste_thread = [MonThreadDeCalcul2(
                        self, self.image, self.motifs_auto[self.indexMotif], self.imageAffichee)]
            elif self.methode_thread == 3:  # pour l'instant celle qui foncitonne le mieux
                timer = QTimer.singleShot(5, self.detecteUnPoint)

    def picture_detect(self):
        """
        Est lancée lors de la détection automatique des points. Gère l'ajout des thread de calcul.
        self.motifs_autos : tableau des motifs
        """
        self.dbg.p(1, "rentre dans 'picture_detect'")
        self.dbg.p(3, "début 'picture_detect'" + str(self.indexMotif))
        if self.index <= self.image_max:
            self.pointsFound = []
            if self.indexMotif <= len(self.motifs_auto) - 1:
                self.dbg.p(1, "'picture_detect' : While")
                self.pointTrouve = filter_picture(
                    self.motifs_auto, self.indexMotif, self.imageAffichee, self.listePoints)
                self.dbg.p(3, "Point Trouve dans mon Thread : " +
                           str(self.pointTrouve))
                self.onePointFind()
                self.indexMotif += 1
            else:
                self.indexMotif = 0
        if self.index == self.image_max:
            if self.indexMotif == 0 and not self.goCalcul:  # dernier passage
                self.stopCalculs.emit()
            elif self.indexMotif == 0 and self.goCalcul:  # premier passage, premier calcul de la dernière image
                self.goCalcul = False

    def stopComputing(self):
        self.dbg.p(1, "rentre dans 'stopComputing'")
        self.pileDeDetections = []  # vide la liste des points à détecter encore
        self.setEnabled(1)
        self.pushButton_stopCalculs.setEnabled(0)
        self.pushButton_stopCalculs.hide()
        # rétablit les fonctions du spinbox et du slider pour gérer l'image
        self.active_controle_image()
        self.app.recalculLesCoordonnees()
        return

    def onePointFind(self):
        """est appelée quand un point a été trouvé lors de la détection automatique
        self.pointFound : liste des points trouvés
        """
        self.dbg.p(1, "rentre dans 'onePointFind'")
        self.pointsFound.append(self.pointTrouve)  # stock all points found
        for point in self.pointsFound:
            self.storePoint(vecteur(point[0], point[1]))

    def pointEnMetre(self, p):
        """
        renvoie un point, dont les coordonnées sont en mètre, dans un
        référentiel "à l'endroit"
        @param p un point en "coordonnées d'écran"
        """
        self.dbg.p(1, "rentre dans 'pointEnMetre'")
        return vecteur(
            self.sens_X * float(p.x - self.origine.x) * self.echelle_image.mParPx(),
            self.sens_Y * float(self.origine.y - p.y) * self.echelle_image.mParPx())

    def enregistre_ui(self):
        self.dbg.p(1, "rentre dans 'enregistre_ui'")
        if not self.vide and  self.echelle_faite:
            base_name = os.path.splitext(os.path.basename(self.filename))[0]
            defaultName = os.path.join(DOCUMENT_PATH[0], base_name+'.mecavideo')
            fichier = QFileDialog.getSaveFileName(
                self,
                _translate("pymecavideo", "Enregistrer le projet pymecavideo", None),
                defaultName,
                _translate("pymecavideo", "Projet pymecavideo (*.mecavideo)", None))
            self.enregistre(fichier[0])
        else :
            QMessageBox.critical(None, _translate("pymecavideo", "Erreur lors de l'enregistrement", None), _translate("pymecavideo", "Il manque les données, ou l'échelle", None), QMessageBox.Ok, QMessageBox.Ok)
        return
    
    def enregistre(self, fichier):
        """
        Enregistre les données courantes dans un fichier,
        à un format CSV, séparé par des tabulations
        """
        self.dbg.p(1, "rentre dans 'enregistre'")
        sep_decimal = "."
        if locale.getdefaultlocale()[0][0:2] == 'fr':
            # en France, le séparateur décimal est la virgule
            sep_decimal = ","
        if not fichier:
            return
        with open(fichier, 'w') as outfile:
            message = _translate(
                "pymecavideo", "temps en seconde, positions en mètre", None)
            outfile.write(self.entete_fichier(message))
            self.echelle = self.echelle_image.pxParM()
            donnees = self.csv_string(
                sep = "\t", unite = "m",
                debut = self.premiere_image_pointee,
                origine = self.origine
            ).replace(".",sep_decimal)
            outfile.write(donnees)
        self.modifie = False
        return

    def entete_fichier(self, msg=""):
        self.dbg.p(1, "rentre dans 'entete_fichier'")
        return f"""\
#pymecavideo
#video = {self.filename}
#sens axe des X = {self.sens_X}
#sens axe des Y = {self.sens_Y}
#largeur video = {self.width()}
#hauteur video = {self.height()}
#rotation = {self.rotation}
#origine de pointage = {self.origine}
#index de depart = {self.premiere_image_pointee}
#echelle {self.echelle_image.longueur_reelle_etalon} m pour {self.echelle_image.longueur_pixel_etalon()} pixel
#echelle pointee en {self.echelle_image.p1 if self.echelle_faite else None} {self.echelle_image.p2 if self.echelle_faite else None}
#intervalle de temps : {self.deltaT}
#suivi de {self.nb_obj} point(s)
#{msg}
#"""

    def affiche_image_spinbox(self):
        self.dbg.p(1, "rentre dans 'affiche_image_spinbox'")
        if self.lance_capture:
            if self.spinBox_image.value() < self.index:
                # si le point est sur une image, on efface le point
                if self.spinBox_image.value() == self.index:
                    for i in range(self.nb_obj):
                        self.efface_point_precedent()
            if self.spinBox_image.value() > self.index:
                # on refait le point
                if self.spinBox_image.value() <= self.index:
                    for i in range(self.nb_obj):
                        self.refait_point_suivant()
        self.index = self.spinBox_image.value()
        self.affiche_image()
        return

    def vecteursVitesse(self, echelle_vitesse):
        """
        Calcule les vecteurs vitesse affichables étant donné la collection
        de points. Un vecteur vitesse a pour origine un point de la 
        trajectoire, et sa direction, sa norme sont basées sur le point
        précédent et le point suivant ; il faut donc au moins trois pointages
        pour que le résultat ne soit pas vide.

        @param echelle_vitesse le nombre de pixels pour 1 m/s
        @return un dictionnaire objet => [(org, ext), ...] où org et ext
          sont l'origine et l'extrémité d'un vecteur vitesse
        """
        result = {obj : [] for obj in self.suivis}
        trajectoires = {obj: [self.data[t][obj] for t in self.dates if self.data[t][obj] is not None] for obj in self.suivis}
        for obj in self.suivis:
            precedent = trajectoires[obj][0]
            suivant = None
            for i in range(1, len(trajectoires[obj]) - 1):
                # itération le long de la trajectoire, sauf
                # sur les points extrêmes.
                if suivant:
                    point = suivant # le point est l'ancien suivant s'il existe
                else:
                    point = trajectoires[obj][i]
                suivant = trajectoires[obj][i+1]
                vitesse = (self.pointEnMetre(suivant) - self.pointEnMetre(precedent)) * (1 / self.deltaT / 2)
                # attention, l'axe Y de l'écran est vers le bas !!
                if self.sens_Y == 1: vitesse.miroirY()
                result[obj].append ((point, point + (vitesse * echelle_vitesse)))
                precedent = point # on conserve les coordonnées pour la suite
        return result

