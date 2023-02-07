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

from PyQt6.QtCore import QThread, pyqtSignal, QLocale, QTranslator, Qt, \
    QSize, QTimer, QObject, QRect, QPoint, QPointF
from PyQt6.QtGui import QKeySequence, QIcon, QPixmap, QImage, QPainter, \
    QCursor, QPen, QColor, QFont, QResizeEvent, QShortcut
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QLayout, \
    QFileDialog, QTableWidgetItem, QInputDialog, QLineEdit, QMessageBox, \
    QTableWidgetSelectionRange

import os, time, re
import locale

from version import Version
from vecteur import vecteur
from echelle import Echelle_TraceWidget
from image_widget import ImageWidget
from pointage import Pointage
from globdef import _translate, cible_icon, DOCUMENT_PATH, inhibe
from cadreur import openCvReader
from toQimage import toQImage
from suivi_auto import SelRectWidget
from detect import filter_picture

import interfaces.icon_rc

class VideoPointeeWidget(ImageWidget, Pointage):
    """
    Cette classe permet de gérer une séquence d'images extraites d'une vidéo
    et les pointages qu'on peut réaliser à la souris ou automatiquement,
    pour suivre les mouvements d'un ou plusieurs objets.
    """

    def __init__(self, parent):
        #ImageWidget.__init__(self, parent)
        Pointage.__init__(self)
        self.app = None                 # la fenêtre principale
        self.dbg = None                 # le débogueur
        self.prefs = None               # les préférences
        self.hotspot = None             # vecteur (position de la souris)
        self.image = None               # l'image tirée du film
        self.image_w = self.width()     # deux valeurs par défaut
        self.image_h = self.height()    # pas forcément pertinentes
        self.setMouseTracking(True)     # on réagit aux mouvement de souris
        self.origine = vecteur(self.width()//2, self.height()//2)
        self.couleurs = [
            "red", "blue", "cyan", "magenta", "yellow", "gray", "green"] *2
        self.tourne = False        # au cas où on fait tourner les images
        self.premier_resize = True # devient faux après redimensionnement
        self.rotation = 0          # permet de retourner une vidéo mal prise
        self.image_max = None      # numéro de la dernière image de la vidéo
        self.framerate = None      # nombre d'images par seconde
        # dimensions natives des images de la vidéo
        self.largeurFilm, self.hauteurFilm = None, None
        self.index = None          # index de l'image courante
        self.objet_courant = 1     # désignation de l'objet courant
        self.filename = None       # le nom du fichier vidéo
        self.a_une_image = False   # indication quant à une image disponible
        self.imageExtraite = None  # référence de l'image courante
        self.lance_capture = False # un pointage est en cours
        self.echelle_trace = None  # widget pour tracer l'échelle
        self.selRect = None        # un objet gérant la sélection par rectangle
        self.lance_cature = False  # devient vrai quand on commence à pointer
        self.auto = False          # devient vrai pour le pointage automatique
        self.motifs_auto = []      # liste de motifs pour le suivi auto
        self.pointsProbables = {}  # dict. de points proches de la détection ?
        self.refait_point = False  # on doit repointer une date
        self.pointageOK = False    # il est possible de faire un pointage
        self.pointageCursor = None # le curseur pour le pointage
        
       # fait un beau gros curseur
        cible_pix = QPixmap(cible_icon).scaledToHeight(32)
        self.pointageCursor = QCursor(cible_pix)

        self.connecte_signaux()
        return


    # signaux de la classe
    clic_sur_video_signal = pyqtSignal()
    selection_motif_done = pyqtSignal()
    stopCalculs = pyqtSignal()
    dimension_data = pyqtSignal(int)

    def connecte_signaux(self):
        """
        Connecte les signaux spéciaux
        """
        # connexion des signaux spéciaux
        self.clic_sur_video_signal.connect(self.clic_sur_la_video)
        self.selection_motif_done.connect(self.suiviDuMotif)
        self.stopCalculs.connect(self.stopComputing)
        self.dimension_data.connect(self.redimensionne_data)
        return

    def __str__(self):
        """
        donne une vision partielle de l'instance courante
        """
        result = {a : str(getattr(self,a)) for a in dir(self) \
                  if not callable(getattr(self,a)) and \
                  not isinstance(getattr(self,a), QObject)}
        
        return f"VideoPointeeWidget({result})"
    
    def setApp(self, app):
        """
        Connecte le videoWidget à sa fenêtre principale, son débogueur
        et ses préférences
        """
        self.app = app
        self.dbg = app.dbg
        self.prefs = app.prefs
        return
   
    def redimensionne_data(self, dim):
        """
        redimensionne self.data (fonction de rappel connectée au signal
        self.dimension_data)
        @param dim la nouvelle dimension des données
          (en nombre d'objets à suivre)
        """
        self.dbg.p(2, "rentre dans 'redimensionne_data'")
        if self.image_max and self.deltaT:
            self.dimensionne(dim, self.deltaT, self.image_max)
            # self.app.cree_tableau(nb_suivis = self.nb_obj)
        return

    @property
    def nb_obj(self):
        """
        @return le nombre d'objets suivis
        """
        if self.suivis is None: return 0
        return len(self.suivis)
    
    def clear(self):
        self.image = None
        return

    def placeImage(self, im, ratio):
        """
        place une image dans le widget, en conservant le ratio de cette image
        @param im une image
        @param ratio le ratio à respecter
        @return l'image, redimensionnée selon le ratio
        """
        self.dbg.p(2, "rentre dans 'placeImage'")
        self.image_w = min(self.width(), round(self.height() * ratio))
        self.image_h = round(self.image_w / ratio)
        self.echelle = self.image_w / self.largeurFilm
        self.setMouseTracking(True)
        image = im.scaled(self.image_w, self.image_h)
        self.setImage(image)
        self.reinit_origine()
        return image
    
    def reinit_origine(self):
        """
        Replace l'origine au centre de l'image
        """
        self.origine = vecteur(self.image_w//2, self.image_h//2)
        return

    def maj(self, tourne=False):
        if tourne:
            self.tourne = True
        return

    def resizeEvent(self, e):
        self.dbg.p(2, "rentre dans 'resizeEvent'")
        if self.premier_resize:  # Au premier resize, la taille est changée mais pas l'origine.
            self.premier_resize = False
            self.reinit_origine()

        if e.oldSize() != QSize(-1, -1):
            if not self.tourne:
                ratiow = self.width()/e.oldSize().width()
                ratioh = self.height()/e.oldSize().height()
            else:
                ratiow = self.width()/e.oldSize().height()
                ratioh = self.height()/e.oldSize().width()
            x = self.origine.x*ratiow
            y = self.origine.y*ratioh
            if not self.app.premier_chargement_fichier_mecavideo:
                self.origine = vecteur(x, y)
        return

    def storePoint(self, point):
        """
        enregistre un point, quand self.index et self.objet_courant
        sont déjà bien réglés.
        @param point la position à enregistrer
        """
        self.dbg.p(2, "rentre dans 'storePoint'")
        if self.lance_capture or self.auto:
            self.pointe(self.objet_courant, point, index=self.index-1)
            self.clic_sur_video_signal.emit()
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
            # on revient à l'état D sauf en cas de suivi automatique
            # auquel cas l'état B perdure
            if not self.auto:
                self.app.change_etat.emit("D")
            else:
                # on reste dans l'état B, néanmoins on synchronise
                # les contrôles de l'image
                self.app.image_n.emit(self.index)
        return

    def mouseReleaseEvent(self, event):
        """
        enregistre le point de l'évènement souris, si self.pointageOK
        est vrai ; voir self.extract_image pour voir les conditions
        de validité.

        Si self.refait_point est vrai (on a été délégué depuis un
        bouton refaire, du tableau de coordonnées, alors on rebascule
        éventuellement vers l'onglet coordonnées, quand le dernier
        objet a été pointé.
        """
        if self.pointageOK and event.button() == Qt.MouseButton.LeftButton:
            self.app.change_etat.emit("E")
            self.pointe(
                self.objet_courant, event, index=self.index-1)
            self.objetSuivant()
            self.clic_sur_video_signal.emit()
            self.app.update_zoom.emit(self.hotspot)
            self.update()
            if self.refait_point : # on a été délégué pour corriger le tableau
                if self.objet_courant == self.suivis[0]:
                    # le dernier objet est pointé, retour au tableau de coords
                    self.refait_point = False
                    self.app.show_coord.emit()
        return

    def mouseMoveEvent(self, event):
        if self.app.etat in ("A","D", "E"):
            p = vecteur(qPoint = event.position())
            self.hotspot = p
            self.app.update_zoom.emit(self.hotspot)
        return
    
    def paintEvent(self, event):
        if self.image:
            if self.app.etat in ("A", "C", "D", "E") and \
               self.hotspot is not None:
                self.app.update_zoom.emit(self.hotspot)
            painter = QPainter()
            painter.begin(self)
            ############################################################
            # mise en place de l'image
            if self.image is not None: painter.drawPixmap(0, 0, self.image)

            ############################################################
            # dessin de l'origine
            longueur_origine = 5
            painter.setPen(QColor("green"))
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
            painter.setPen(QColor("green"))
            painter.translate(0, 0)
            painter.translate(round(self.origine.x), round(self.origine.y))
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
        extrait une image de la video à l'aide d'OpenCV ; met à jour
        self.pointageOK s'il est licite de pointer dans l'état actuel;
        met à jour le curseur à utiliser aussi
        @param index le numéro de l'image (commence à 1)

        @return un boolen (ok), et l'image au format d'openCV ; l'image
          au bon format pour Qt est dans self.imageExtraite
        """
        self.dbg.p(2, "rentre dans 'extract_image' " + 'index : ' + str(index))
        ok, image_opencv = self.cvReader.getImage(index, self.rotation)
        if not ok:
            self.affiche_barre_statut(
                _translate("pymecavideo", "Pymecavideo n'arrive pas à lire l'image", None))
            return False, None
        self.a_une_image = ok
        self.imageExtraite = toQImage(image_opencv)
        # il est licite de pointer dans l'état D à condition
        # qu'il n'y ait encore aucun pointage, ou que l'index soit
        # connexe aux pointages existants
        self.pointageOK = \
            self.app.etat in ("D", "E") and \
            (not self or index in range(self.premiere_image() - 1, \
                                        self.derniere_image() + 2))
        if self.pointageOK:
            # beau gros curseur seulement si le pointage est licite ;
            self.setCursor(self.pointageCursor)
        else:
            self.setCursor(Qt.CursorShape.ArrowCursor)
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
        self.dbg.p(2, "rentre dans 'calcul_deltaT'")
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
    
    def rouvre(self):
        """
        Ici c'est la partie dévolue au videoWidget quand on rouvre un
        fichier pymecavideox
        """
        self.app.sens_axes.emit(self.sens_X, self.sens_Y)
        self.framerate, self.image_max, self.largeurFilm, self.hauteurFilm = \
            self.cvReader.recupere_avi_infos(self.rotation)
        self.ratio = self.largeurFilm / self.hauteurFilm
        return

    def restaure_pointages(self, data, premiere_image_pointee) :
        """
        Rejoue les pointages issus d'un fichier pymecavideo
        @param data une liste de listes de type [t, x1, y1, ..., xn, yn]
        @param premiere_image_pointee la toute première image pointée
          (au moins 1)
        """
        self.dimensionne(self.nb_obj, self.deltaT, self.image_max)
        for i in range(len(data)) :
            for obj in self.suivis:
                j = int(obj)*2-1 # index du début des coordonnées xj, yj
                if len(data[i]) > j:
                    x, y = data[i][j:j + 2]
                    # À ce stade x et y sont en mètre
                    # on remet ça en pixels
                    x = self.origine.x + self.sens_X * \
                        round(float(x) * self.echelle_image.pxParM())
                    y = self.origine.y - self.sens_Y * \
                        round(float(y) * self.echelle_image.pxParM())
                    self.pointe(
                        obj, vecteur(x, y),
                        index = i + premiere_image_pointee - 1)
        # affiche la dernière image pointée
        der = self.derniere_image()
        if der is not None:
            if der < self.image_max:
                self.index = der + 1
            else:
                self.index = self.image_max
        else:
            self.index = 1
        self.clic_sur_video_ajuste_ui()
        self.app.echelle_modif.emit(self.tr("Refaire l'échelle"), "background-color:orange;")
        return
    
    def init_image(self):
        """
        initialise certaines variables lors le la mise en place d'une 
        nouvelle vidéo
        """
        self.dbg.p(2, "rentre dans 'init_image'")
        self.index = 1
        self.extract_image(1)
        self.framerate, self.image_max, self.largeurFilm, self.hauteurFilm = \
            self.cvReader.recupere_avi_infos(self.rotation)
        self.ratio = self.largeurFilm / self.hauteurFilm
        self.calcul_deltaT()
        # on dimensionne les données pour les pointages
        self.redimensionne_data(self.nb_obj)
        self.affiche_image()
        return

    def affiche_image(self, index= None):
        '''
        À condition qu'on ait ouvert le fichier vidéo,
        extrait l'image courante ou l'image spécifiée
        par l'index, et affiche cette image
        @param index permet de modifier l'image courante si c'est un entier
          (None par défaut)
        '''
        if not self.filename:
            return
        if index is not None: self.index = index
        self.dbg.p(2, f"rentre dans 'affiche_image' self.index = {self.index} self.image_max = {self.image_max}")
        if self.index <= self.image_max:
            self.extract_image(self.index)  # 2ms
            self.placeImage(self.imageExtraite, self.ratio)
        elif self.index > self.image_max:
            self.index = self.image_max
            self.lance_capture = False
        return
    
    def init_cvReader(self):
        """
        Initialise le lecteur de flux vidéo pour OpenCV
        et recode la vidéo si nécessaire.
        """
        self.dbg.p(2, "rentre dans 'init_cvReader', ouverture de %s" %
                   (self.filename))
        self.cvReader = openCvReader(self.filename)
        time.sleep(0.1)
        if not self.cvReader.ok:
            QMessageBox.warning(None, "Format vidéo non pris en charge",
                                _translate("pymecavideo", """\le format de cette vidéo n'est pas pris en charge par pymecavideo""",
                                           None))
        else:
            return True

    def openTheFile(self, filename):
        """
        Ouvre le fichier de nom filename, enregistre les préférences de
        fichier vidéo.
        @param filename nom du fichier
        """
        self.dbg.p(2, "rentre dans 'openTheFile'")
        if not filename :
            return
        self.filename = filename
        goOn = self.init_cvReader()
        if goOn:  # le fichier vidéo est OK, et son format est reconnu
            self.init_image()
            self.app.change_etat.emit("A")
        else:
            QMessageBox.warning(
                None,
                _translate("pymecavideo", "Erreur lors de la lecture du fichier", None),
                _translate("pymecavideo", "Le fichier<b>{0}</b> ...\nn'est peut-être pas dans un format vidéo supporté.", None).format(
                    filename))
        return
    
    def affiche_point_attendu(self, obj):
        """
        Renseigne sur le numéro d'objet du point attendu
        affecte la ligne de statut et la ligne sous le zoom
        @param obj l'objet courant
        """
        self.dbg.p(2, "rentre dans 'affiche_point_attendu'")
        self.app.affiche_statut.emit(self.tr("Cliquez sur l'objet : {0}").format(obj))
        return

    def clic_sur_la_video(self):
        self.dbg.p(2, "rentre dans 'clic_sur_video'")
        self.purge_defaits() # oublie les pointages à refaire
        self.clic_sur_video_ajuste_ui()
        return
    
    def clic_sur_video_ajuste_ui(self):
        """
        Ajuste l'interface utilisateur pour attendre un nouveau clic
        """
        self.dbg.p(2, "rentre dans 'clic_sur_video_ajuste_ui'")
        self.affiche_image()
        self.affiche_point_attendu(self.objet_courant)
        self.app.enableDefaire(self.peut_defaire())
        self.app.enableRefaire(self.peut_refaire())
        return

    def capture_auto(self):
        """
        fonction appelée au début de l'état AB : prépare la sélection
        des motifs à suivre en capture automatique
        """
        self.dbg.p(2, "rentre dans 'capture_auto'")
        self.auto = True # inhibe le pointage à la souris !
        # recouvre l'image avec le widget selRect pour définir des
        # rectangles pour chaque motif à suivre
        self.selRect = SelRectWidget(self)
        self.selRect.show()
        return

    def feedbackEchelle(self, p1, p2):
        """
        affiche une trace au-dessus du self.job, qui reflète les positions
        retenues pour l'échelle
        """
        self.dbg.p(2, "rentre dans 'feedbackEchelle'")
        if self.echelle_trace:
            self.echelle_trace.hide()
        self.echelle_trace = Echelle_TraceWidget(self, p1, p2)
        # on garde les valeurs pour le redimensionnement
        self.echelle_trace.show()
        if self.echelle:
            self.app.echelle_modif.emit(self.tr("Refaire l'échelle"), "background-color:orange;")
        return

    def reinitialise_capture(self):
        """
        Efface toutes les données de la capture en cours et prépare une nouvelle
        session de capture. Retourne à l'état A
        """
        self.dbg.p(2, "rentre dans 'reinitialise_capture'")
        # oublie self.echelle_image
        self.clearEchelle()
        if self.echelle_trace is not None:
            self.echelle_trace.hide()
        self.echelle_trace = None
        self.app.echelle_modif.emit(self.tr("Définir l'échelle"),
                                    "background-color:None;")

        # reinitialisation du widget video
        self.setCursor(Qt.CursorShape.ArrowCursor)
        self.setEnabled(True)
        self.reinit_origine()
        self.pointsProbables = {}
        self.motifs_auto = []
        # retire les objets déjà pointés
        self.redimensionne_data(self.nb_obj)
        self.sens_X = self.sens_Y = 1
        self.app.sens_axes.emit(self.sens_X, self.sens_Y)
        self.app.defixeLesDimensions()
        self.app.change_etat.emit("A")
        return
    
    def suiviDuMotif(self):
        self.dbg.p(2, "rentre dans 'suiviDuMotif'")
        if len(self.motifs_auto) == self.nb_obj:
            self.dbg.p(3, "selection des motifs finie")
            self.selRect.hide()
            self.indexMotif = 0
            self.pileDeDetections = []
            for i in range(self.index, self.image_max+1):
                self.pileDeDetections.append(i)
            self.dbg.p(3, "self.pileDeDetections : %s" % self.pileDeDetections)
            self.app.change_etat.emit("B")
        return

    # @time_it
    def detecteUnPoint(self):
        """
        méthode (re)lancée pour les détections automatiques de points
        traite une à une les données empilées dans self.pileDeDetections
        et relance un signal si la pile n'est pas vide après chacun
        des traitements.
        """
        self.dbg.p(2, f"rentre dans 'detecteUnPoint', pileDeDetection = {self.pileDeDetections}")
        if self.pileDeDetections:
            # on dépile un index de détections à faire et on met à jour
            # le bouton de STOP
            self.app.stop_n.emit(f"STOP ({self.pileDeDetections.pop(0)})")
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
            # programme le suivi du point suivant après un délai de 50 ms,
            # pour laisser une chance aux évènement de l'interface graphique
            # d'être traités en priorité
            QTimer.singleShot(50, self.detecteUnPoint)
        else:
            # fin de la détection automatique
            self.auto = False
            # si la pile d'images à détecter a été vidée par self.stopComputing,
            # il faut passer à l'image suivante si possible
            self.clic_sur_video_signal.emit()
            self.app.change_etat.emit("D")
        return

    def stopComputing(self):
        self.dbg.p(2, "rentre dans 'stopComputing'")
        self.pileDeDetections = []  # vide la liste des points à détecter encore
        # la routine self.detecteUnPoint reviendra à l'état D après que
        # le dernier objet aura été détecté
        return

    def enregistre_ui(self):
        self.dbg.p(2, "rentre dans 'enregistre_ui'")
        if self.data and self.echelle_image:
            base_name = os.path.splitext(os.path.basename(self.filename))[0]
            defaultName = os.path.join(DOCUMENT_PATH, base_name+'.mecavideo')
            fichier = QFileDialog.getSaveFileName(
                self,
                _translate("pymecavideo", "Enregistrer le projet pymecavideo", None),
                defaultName,
                _translate("pymecavideo", "Projet pymecavideo (*.mecavideo)", None))
            self.enregistre(fichier[0])
        else :
            QMessageBox.critical(None, _translate("pymecavideo", "Erreur lors de l'enregistrement", None), _translate("pymecavideo", "Il manque les données, ou l'échelle", None))
        return
    
    def enregistre(self, fichier):
        """
        Enregistre les données courantes dans un fichier,
        à un format CSV, séparé par des tabulations
        """
        self.dbg.p(2, "rentre dans 'enregistre'")
        sep_decimal = "."
        if locale.getdefaultlocale()[0][0:2] == 'fr':
            # en France, le séparateur décimal est la virgule
            sep_decimal = ","
        if not fichier:
            return
        # mise à jour des préférences, afin d'en faire aussi l'en-tête
        # pour le fichier pymecavideo
        self.savePrefs()
        with open(fichier, 'w') as outfile:
            message = _translate(
                "pymecavideo", "temps en seconde, positions en mètre", None)
            outfile.write(self.entete_fichier(message))
            donnees = self.csv_string(
                sep = "\t", unite = "m",
                debut = self.premiere_image(),
                origine = self.origine
            ).replace(".",sep_decimal)
            outfile.write(donnees)
        return

    def savePrefs(self):
        d = self.prefs.defaults
        d['version'] = f"pymecavideo {Version}"
        d['proximite'] = str(self.app.radioButtonNearMouse.isChecked())
        d['lastvideo'] = self.filename
        d['videodir'] = os.path.dirname(self.filename)
        d['niveaudbg'] = str(self.dbg.verbosite)
        d['sens_x'] = str(self.sens_X)
        d['sens_y'] = str(self.sens_Y)
        d['taille'] = str((self.app.size().width(),self.app.size().height()))
        d['rotation'] = str(self.rotation)
        d['origine'] = f"({round(self.origine.x)}, {round(self.origine.y)})"
        d['index_depart'] = str(self.premiere_image())
        d['etalon_m'] = str(self.echelle_image.longueur_reelle_etalon)
        d['etalon_px'] = str(self.echelle_image.longueur_pixel_etalon())
        d['etalon_org'] = self.echelle_image.p1.toIntStr() \
            if self.echelle_image else "None"
        d['etalon_ext'] = self.echelle_image.p2.toIntStr() \
            if self.echelle_image else "None"
        d['deltat'] = str(self.deltaT)
        d['nb_obj'] = str(len(self.suivis))
        self.prefs.save()
        
    def entete_fichier(self, msg=""):
        """
        Crée l'en-tête du fichier pymecavideo
        On recopie sous forme de commentaires préfixée par "# "
        tout le fichier de configuration sauf la ligne "[DEFAULT]"
        puis on ajoute le message
        @param msg le message
        @return le texte de l'en-tête (multi-ligne)
        """
        self.dbg.p(2, "rentre dans 'entete_fichier'")
        config = open(self.prefs.conffile).readlines()
        return "".join(["# "+l for l in config[1:]]) + "# " + msg + "\n"

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
        self.dbg.p(2, "rentre dans 'vecteursVitesse'")
        result = {obj : [] for obj in self.suivis}
        trajectoires = self.les_trajectoires()
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

    def apply_preferences(self, rouvre=False):
        """
        Récupère les préférences sauvegardées, et en applique les données
        ici on s'occupe de ce qui se gère facilement au niveau du widget
        video
        @param rouvre est vrai quand on ouvre un fichier pymecavideo ; 
          il est faux par défaut
        """
        self.dbg.p(2, "rentre dans 'VideoWidget.apply_preferences'")
        d = self.prefs.config["DEFAULT"]
        self.filename = d["lastvideo"]
        if os.path.isfile(self.filename):
            self.openTheFile(self.filename)
        else:
            # si le fichier video n'existe pas, inutile d'aller plus
            # loin dans la restauration des données !
            return
        self.sens_X = d.getint("sens_x")
        self.sens_Y = d.getint("sens_y")
        self.rotation = d.getint("rotation")
        self.origine = self.prefs.config.getvecteur("DEFAULT", "origine")
        self.reinitialise_capture()
        if rouvre:
            # dans ce cas on est en train de réouvrir un fichier pymecavideo
            # et on considère plus de données
            #!!!! self.premiere_image_pointee = d.getint("index_depart")
            self.deltatT = d.getfloat("deltat")
            self.dimensionne(d.getint("nb_obj"), self.deltaT, self.image_max)
            self.echelle_image.longueur_reelle_etalon = d.getfloat('etalon_m')
            p1 = self.prefs.config.getvecteur("DEFAULT", "etalon_org")
            p2 = self.prefs.config.getvecteur("DEFAULT", "etalon_ext")
            if p1 != vecteur(0,0) and p2 != vecteur(0,0):
                self.echelle_image.p1 = p1
                self.echelle_image.p2 = p2
            else:
                self.echelle_image.p1 = None
                self.echelle_image.p2 = None
        # choche les cases du sens des axes
        self.app.sens_axes.emit(self.sens_X, self.sens_Y)
        return

    def efface_point_precedent(self):
        """
        revient au point précédent
        """
        self.dbg.p(2, "rentre dans 'efface_point_precedent'")
        if inhibe("defaire",100): return # corrige un bug de Qt 5.15
        if not self.peut_defaire(): return
        self.defaire()
        # dernière image à afficher
        der = self.derniere_image()
        if der:
            self.index = self.derniere_image() + 1
        else:
            self.purge_defaits() # si on a retiré le dernier pointage visible
            if self.index > 1: self.index -= 1
        self.clic_sur_video_ajuste_ui()
        return
    
    def refait_point_suivant(self):
        """rétablit le point suivant après un effacement
        """
        self.dbg.p(2, "rentre dans 'refait_point_suivant'")
        if inhibe("refaire",100): return # corrige un bug de Qt 5.15
        self.refaire()
        # ce serait moins long de remettre juste une ligne dans le tableau
        self.app.recalculLesCoordonnees()
        if self.index < self.image_max:
            self.index += 1
        self.clic_sur_video_ajuste_ui()
        return

    def refait_point_depuis_tableau(self, qpbn ):
        """
        fonction de rappel déclenchée quand on clique dans la dernière
        colonne du tableau
        @param qbbn le bouton qui a été cliqué pour en arriver là
        """
        self.dbg.p(2, "rentre dans 'refait_point_depuis_tableau'")
        self.refait_point=True
        self.objet_courant = self.suivis[0]
        self.index = qpbn.index_image
        self.clic_sur_video_ajuste_ui()
        self.app.show_video.emit()
        return

