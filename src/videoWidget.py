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
        self.couleurs = [
            "red", "blue", "cyan", "magenta", "yellow", "gray", "green"] *2

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

    def resizeEvent(self, e):
        self.dbg.p(2, "rentre dans 'resizeEvent'")
        self.pw.update_imgedit.emit(
            self.image_w, self.image_h, self.rotation)
        if e.oldSize() != QSize(-1, -1):
            ratiow = self.width()/e.oldSize().width()
            ratioh = self.height()/e.oldSize().height()
            self.pw.update_origine.emit(ratiow, ratioh)
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
        if event.button() == Qt.MouseButton.LeftButton:
            self.pw.fin_pointage_manuel.emit(event)
        return

    def mouseMoveEvent(self, event):
        if self.pw.etat in ("A", "AB", "D", "E"):
            p = vecteur(qPoint = event.position())
            self.pw.hotspot = p
            self.pw.update_zoom.emit(self.pw.hotspot)
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
                5, "In videoWidget, paintEvent, self.pw.data :%s" % self.pw.data)
            if self.pw.data:
                for date in self.pw.data:
                    for obj in self.pw.data[date]:
                        point = self.pw.data[date][obj]
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
                round(self.pw.origine.x) + 5, round(self.pw.origine.y) + 15, "O")
            painter.translate(0, 0)
            painter.translate(round(self.pw.origine.x), round(self.pw.origine.y))
            p1 = QPoint(round(self.pw.sens_X * (-40)), 0)
            p2 = QPoint(round(self.pw.sens_X * (40)), 0)
            p3 = QPoint(round(self.pw.sens_X * (36)), 2)
            p4 = QPoint(round(self.pw.sens_X * (36)), -2)
            painter.scale(1, 1)
            painter.drawPolyline(p1, p2, p3, p4, p2)
            painter.rotate(self.pw.sens_X * self.pw.sens_Y * (-90))
            painter.drawPolyline(p1, p2, p3, p4, p2)
            painter.end()
        return

    def rouvre(self):
        """
        Ici c'est la partie dévolue au videoWidget quand on rouvre un
        fichier pymecavideox
        """
        # !!!! il faudrait rétablir l'échelle (p,p2), pas sur le videoWidget
        # !!!! mais dans une instance de Echelle_TraceWidget
        self.pw.sens_axes.emit(self.sens_X, self.sens_Y)
        self.framerate, self.image_max, self.largeurFilm, self.hauteurFilm = \
            self.pw.cvReader.recupere_avi_infos(self.rotation)
        self.pw.ratio = self.pw.largeurFilm / self.pw.hauteurFilm
        # réapplique la préférence de deltat, comme openCV peut se tromper
        self.pw.deltaT = float(self.pw.prefs.config["DEFAULT"]["deltat"])
        self.pw.framerate = round(1/self.pw.deltaT)
        return

    def restaure_pointages(self, data, premiere_image_pointee) :
        """
        Rejoue les pointages issus d'un fichier pymecavideo
        @param data une liste de listes de type [t, x1, y1, ..., xn, yn]
        @param premiere_image_pointee la toute première image pointée
          (au moins 1)
        """
        self.pw.dimensionne(self.pw.nb_obj, self.pw.deltaT, self.pw.image_max)
        for i in range(len(data)) :
            for obj in self.pw.suivis:
                j = int(obj)*2-1 # index du début des coordonnées xj, yj
                if len(data[i]) > j:
                    x, y = data[i][j:j + 2]
                    # À ce stade x et y sont en mètre
                    # on remet ça en pixels
                    x = self.pw.origine.x + self.pw.sens_X * \
                        round(float(x) * self.pw.echelle_image.pxParM())
                    y = self.pw.origine.y - self.pw.sens_Y * \
                        round(float(y) * self.pw.echelle_image.pxParM())
                    self.pointe(
                        obj, vecteur(x, y),
                        index = i + premiere_image_pointee - 1)
        # affiche la dernière image pointée
        der = self.pw.derniere_image()
        if der is not None:
            if der < self.pw.image_max:
                self.pw.index = der + 1
            else:
                self.pw.index = self.image_max
        else:
            self.pw.index = 1
        self.pw.prepare_futur_clic()
        self.pw.echelle_modif.emit(self.tr("Refaire l'échelle"), "background-color:orange;")
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
        self.prepare_futur_clic()
        self.pw.show_video.emit()
        return

    def placeImage(self, im, ratio, largeurFilm):
        """
        place une image dans le widget, en conservant le ratio de cette image
        @param im une image
        @param ratio le ratio à respecter
        @param largeurFilm la largeur originale de la video en pixel
        @return l'image, redimensionnée selon le ratio
        """
        self.dbg.p(2, "rentre dans 'placeImage'")
        self.image_w = min(self.width(), round(self.height() * ratio))
        self.image_h = round(self.image_w / ratio)
        self.echelle = self.image_w / largeurFilm
        self.setMouseTracking(True)
        image = im.scaled(self.image_w, self.image_h)
        self.setImage(image)
        return image
    
