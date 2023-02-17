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
from globdef import cible_icon, DOCUMENT_PATH, inhibe
from cadreur import openCvReader
from toQimage import toQImage
from suivi_auto import SelRectWidget
from detect import filter_picture

import interfaces.icon_rc

class VideoPointeeWidget(ImageWidget):
    """
    Cette classe permet de gérer une séquence d'images extraites d'une vidéo
    et les pointages qu'on peut réaliser à la souris ou automatiquement,
    pour suivre les mouvements d'un ou plusieurs objets.
    """

    def __init__(self, parent):
        ImageWidget.__init__(self, parent)
        self.setMouseTracking(True)     # on réagit aux mouvement de souris
        self.index = None          # index de l'image courante
        self.objet_courant = 1     # désignation de l'objet courant
        self.image_w = self.width()     # deux valeurs par défaut
        self.image_h = self.height()    # pas forcément pertinentes
        self.rotation = 0          # permet de retourner une vidéo mal prise
        self.premier_resize = True # devient faux après redimensionnement

        self.connecte_signaux()
        return


    # signaux de la classe
    clic_sur_video_signal = pyqtSignal()
    selection_motif_done = pyqtSignal()

    def connecte_signaux(self):
        """
        Connecte les signaux spéciaux
        """
        # connexion des signaux spéciaux
        self.clic_sur_video_signal.connect(self.clic_sur_la_video)
        self.selection_motif_done.connect(self.suiviDuMotif)
        return

    def __str__(self):
        """
        donne une vision partielle de l'instance courante
        """
        result = {a : str(getattr(self,a)) for a in dir(self) \
                  if not callable(getattr(self,a)) and \
                  not isinstance(getattr(self,a), QObject)}
        
        return f"VideoPointeeWidget({result})"
    
    def setParent(self, w):
        """
        Connecte le videoWidget au widget principal de son onglet,
        et son débogueur ; self.pw devient un pointeur vers ce widget
        @param w le widget principal de l'onglet de pointage
        """
        self.pw = w
        self.dbg = w.dbg
        return
   
    def clear(self):
        self.image = None
        return

    def enterEvent(self,event):
        """
        Quand la souris arrive sur la vidéo, on met des messages pertinents
        dans la barre de statut
        """
        self.pw.affiche_statut.emit("")
        return

    def resizeEvent(self, e):
        self.dbg.p(2, "rentre dans 'resizeEvent'")
        self.pw.pointage.update_imgedit.emit(
            self.image_w, self.image_h, self.rotation)
        if self.premier_resize:  # Au premier resize, la taille est changée mais pas l'origine.
            self.premier_resize = False
            self.reinit_origine()

        if e.oldSize() != QSize(-1, -1):
            ratiow = self.width()/e.oldSize().width()
            ratioh = self.height()/e.oldSize().height()
            x = self.origine.x*ratiow
            y = self.origine.y*ratioh
            if not self.pw.premier_chargement_fichier_mecavideo:
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
            self.pw.label_zoom.emit(self.tr("Pointage ({obj}) ; x, y =").format(obj = self.objet_courant))
        else:
            # on passe à l'image suivante, et on revient au premier objet
            self.objet_courant = self.suivis[0]
            if self.index < self.image_max:
                self.index +=1
            # on revient à l'état D sauf en cas de suivi automatique
            # auquel cas l'état E perdure
            if not self.auto:
                self.pw.change_etat.emit("D")
            else:
                # on reste dans l'état E, néanmoins on synchronise
                # les contrôles de l'image
                self.pw.image_n.emit(self.index)
        
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
            self.pw.change_etat.emit("E")
            self.pointe(
                self.objet_courant, event, index=self.index-1)
            self.objetSuivant()
            self.clic_sur_video_signal.emit()
            self.pw.update_zoom.emit(self.hotspot)
            self.update()
            if self.refait_point : # on a été délégué pour corriger le tableau
                if self.objet_courant == self.suivis[0]:
                    # le dernier objet est pointé, retour au tableau de coords
                    self.refait_point = False
                    self.pw.show_coord.emit()
        return

    def mouseMoveEvent(self, event):
        if self.pw.etat in ("A", "AB", "D", "E"):
            p = vecteur(qPoint = event.position())
            self.hotspot = p
            self.pw.update_zoom.emit(self.hotspot)
        return
    
    def paintEvent(self, event):
        if self.image:
            painter = QPainter()
            painter.begin(self)
            ############################################################
            # mise en place de l'image
            if self.image is not None: painter.drawPixmap(0, 0, self.image)

            ############################################################
            # dessine les pointages passés
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
            # dessine le repere
            painter.setPen(QColor("green"))
            painter.drawText(
                round(self.origine.x) + 5, round(self.origine.y) + 15, "O")
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
            painter.end()
            ############################################################
            # dessine l'échelle
            painter = QPainter()
            painter.begin(self)
            painter.setPen(QColor("red"))
            painter.drawLine(round(self.echelle_image.p1.x),
                             round(self.echelle_image.p1.y),
                             round(self.echelle_image.p2.x),
                             round(self.echelle_image.p2.y))
            painter.end()
        return

    def rouvre(self):
        """
        Ici c'est la partie dévolue au videoWidget quand on rouvre un
        fichier pymecavideox
        """
        self.pw.sens_axes.emit(self.sens_X, self.sens_Y)
        self.framerate, self.image_max, self.largeurFilm, self.hauteurFilm = \
            self.cvReader.recupere_avi_infos(self.rotation)
        self.ratio = self.largeurFilm / self.hauteurFilm
        # réapplique la préférence de deltat, comme openCV peut se tromper
        self.deltaT = float(self.pw.prefs.config["DEFAULT"]["deltat"])
        self.framerate = round(1/self.deltaT)
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
        self.pw.echelle_modif.emit(self.tr("Refaire l'échelle"), "background-color:orange;")
        return
    
    def affiche_point_attendu(self, obj):
        """
        Renseigne sur le numéro d'objet du point attendu
        affecte la ligne de statut et la ligne sous le zoom
        @param obj l'objet courant
        """
        self.dbg.p(2, "rentre dans 'affiche_point_attendu'")
        self.pw.affiche_statut.emit(self.tr("Cliquez sur l'objet : {0}").format(obj))
        return

    def clic_sur_la_video(self):
        self.dbg.p(2, "rentre dans 'clic_sur_video'")
        self.purge_defaits() # oublie les pointages à refaire
        self.clic_sur_video_ajuste_ui()
        self.pw.sync_img2others(self.index)
        return
    
    def clic_sur_video_ajuste_ui(self):
        """
        Ajuste l'interface utilisateur pour attendre un nouveau clic
        """
        self.dbg.p(2, "rentre dans 'clic_sur_video_ajuste_ui'")
        self.affiche_image()
        self.affiche_point_attendu(self.objet_courant)
        self.pw.enableDefaire(self.peut_defaire())
        self.pw.enableRefaire(self.peut_refaire())
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
        self.pw.zoomLabel.setText(self.tr("Zone à suivre n° {zone} x, y =").format(zone=self.suivis[0]))
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
            self.pw.echelle_modif.emit(self.tr("Refaire l'échelle"), "background-color:orange;")
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
            self.pw.change_etat.emit("B")
        else:
            self.pw.label_zoom.emit(self.tr("Zone à suivre n° {zone} x, y =").format(zone=self.suivis[len(self.motifs_auto)]))
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
            self.pw.stop_n.emit(f"STOP ({self.pileDeDetections.pop(0)})")
            ok, image = self.cvReader.getImage(
                self.index, self.rotation, rgb=False)
            # puis on boucle sur les objets à suivre et on
            # détecte leurs positions
            # Ça pourrait bien se faire dans des threads, en parallèle !!!
            for i, part in enumerate(self.motifs_auto):
                self.indexMotif = i
                zone_proche = self.pointsProbables.get(self.objet_courant, None)
                point = filter_picture(part, image, zone_proche)
                self.pointsProbables[self.objet_courant] = point
                echelle = self.image_w / self.largeurFilm
                # on convertit selon l'échelle, et on recentre la détection
                # par rapport au motif `part`
                self.storePoint(vecteur(
                    echelle*(point[0]+part.shape[1]/2),
                    echelle*(point[1]+part.shape[0]/2)))
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
            self.pw.change_etat.emit("D")
        return

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
        config = open(self.pw.prefs.conffile).readlines()
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
        self.pw.show_video.emit()
        return

    def coords(self, p):
        """
        @param p un point, vecteur de coordonnées entières
        @return les valeurs de x, y en px et puis en mètre (formatées :.2e)
        """
        # on se rapporte à l'origine du repère
        p = p - self.origine
        # et aux sens des axes
        p.redresse(self)
        
        if not self.echelle_image:
            return int(p.x), int(p.y), self.tr("indéf."), self.tr("indéf.")
        return int(p.x), int(p.y), \
            f"{p.x/self.echelle_image.pxParM():.2e}", \
            f"{p.y/self.echelle_image.pxParM():.2e}"

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
        self.video.setImage(image)
        self.reinit_origine()
        return image
    
