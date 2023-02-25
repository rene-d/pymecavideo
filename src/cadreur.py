# -*- coding: utf-8 -*-

"""
    cadreur, a module for pymecavideo:
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

import sys
import os
import time
import subprocess
import re
import subprocess
import shutil
import numpy as np
import cv2
from PyQt6.QtCore import QObject, QThread, pyqtSignal, QLocale, QTranslator, Qt, QSize, QTimer, QCoreApplication, QMetaObject
from PyQt6.QtGui import QKeySequence, QIcon, QPixmap, QImage
from PyQt6.QtWidgets import QVBoxLayout, QLabel, QFrame, QGridLayout, QSlider, QDialogButtonBox, QDialog
from vecteur import vecteur
from itertools import cycle


class Cadreur(QObject):
    """
    Un objet capable de recadrer une vidéo en suivant le déplacement
    d'un point donné. 
    Paramètres du constructeur :
    @param obj le numéro de l'objet qui doit rester immobile
    @param app la fenêtre principale
    @param titre le titre désiré pour la fenêtre
    """

    def __init__(self, obj, app, titre=None):
        QObject.__init__(self)
        self.app = app
        self.pointage = app.pointage
        self.video = app.pointage.video
        if titre == None:
            self.titre = str(self.tr("Presser la touche ESC pour sortir"))
        self.obj = obj
        # on fait la liste des index où l'objet a été pointé (début à 0)
        self.index_obj = self.pointage.index_trajectoires(debut = 0)
        self.capture = cv2.VideoCapture(self.pointage.filename)
        self.fps = self.capture.get(cv2.CAP_PROP_FPS)
        self.delay = int(1000.0 / self.fps)
        self.app.dbg.p(2, "In : Video, self.obj %s" %
                       (self.obj))
        self.app.dbg.p(3, "In : Video, __init__, fps = %s and delay = %s" % (
            self.fps, self.delay))

        self.ralenti = 3
        self.fini = False
        self.maxcadre(self.obj)

    def echelleTaille(self):
        """
        Renvoie l'échelle qui permet de passer de l'image dans pymecavideo
        à l'image effectivement trouvée dans le film, et la taille du film
        @return un triplet échelle, largeur, hauteur (de l'image dans le widget de de pymecavideo)
        """
        m = self.pointage.imageExtraite.size()
        echx = 1.0 * m.width() / self.video.image_w
        echy = 1.0 * m.height() / self.video.image_h
        ech = max(echx, echy)
        return ech, int(m.width() / ech), int(m.height() / ech)

    def controleRalenti(self, position):
        """
        fonction de rappel commandée par le bouton "Quitte"
        """
        self.ralenti = max([1, position])

    def maxcadre(self, obj):
        """
        calcule le plus grand cadre qui peut suivre l'objet obj
        sans déborder du cadre de la vidéo. Initialise self.rayons qui indique
        la taille de ce cadre, et self.decal qui est le décalage du point
        à suivre par rapport au centre du cadre.

        Modifie les propriétés :
        - self.tl (top left) coin haut-gauche du cadre
        - self.sz (size) taille du cadre
        - self.decal coordonnées du centre du cadre dans lui-même
        - self.rayons coordonnées du centre du cadre dans son parent
        
        @param obj l'objet autour duquel on doit définir le cadre
        """
        ech, w, h = self.echelleTaille()

        agauche = []
        dessus = []
        for p in self.pointage.gen_iter_traj(obj):
            if p:
                agauche.append(p.x)
                dessus.append(p.y)
        adroite = [w - x - 1 for x in agauche]
        dessous = [h - y - 1 for y in dessus]

        agauche = min(agauche)
        adroite = min(adroite)
        dessus = min(dessus)
        dessous = min(dessous)
        self.tl = vecteur(agauche, dessus)  # topleft
        self.sz = vecteur(adroite + agauche, dessous + dessus)  # size

        self.decal = vecteur((adroite - agauche) / 2, (dessous - dessus) / 2)
        self.rayons = vecteur((agauche + adroite) / 2, (dessus + dessous) / 2)
        return

    def queryFrame(self):
        """
        récupère l'image suivante du film et traite le cas où OpenCV
        ne sait pas le faire
        @return une IplImage
        """
        if cv2.GrabFrame(self.capture):
            return cv2.RetrieveFrame(self.capture)
        else:
            print(
                "erreur, OpenCV 2.1 ne sait pas extraire des images du fichier", videofile)
            sys.exit(1)

    def montrefilm(self):
        """
        Calcule et montre le film recadré à l'aide d'OpenCV
        """
        self.dialog = RalentiWidget(parentObject=self)
        self.dialog.exec()

    def rotateImage(self, img, angle):
        if angle == 90:
            return cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
        elif angle == 270:
            return cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)
        elif angle == 180:
            return cv2.rotate(img, cv2.ROTATE_180)
        else:
            return img  # angle=0

from interfaces.Ui_ralenti_dialog import Ui_Dialog as Ralenti_Dialog

class RalentiWidget(QDialog, Ralenti_Dialog):

    """Affiche le film recadré"""

    def __init__(self, parentObject):
        QDialog.__init__(self)
        Ralenti_Dialog.__init__(self)
        self.cadreur = parentObject
        self.pointage = parentObject.pointage
        self.ralenti = 1
        self.images   = cycle(self.cadreur.index_obj)
        self.origines = cycle((p for p in self.pointage.gen_iter_traj(self.cadreur.obj) if p))
        self.delay = self.cadreur.delay
        self.ech, self.w, self.h = self.cadreur.echelleTaille()
        self.timer = QTimer()
        self.timer.setInterval(int(self.delay * self.ralenti))
        self.timer.timeout.connect(self.affiche_image)

        self.setupUi(self)
        self.pushButton.clicked.connect(self.reject)
        self.horizontalSlider.valueChanged.connect(self.change_ralenti)
        self.label.resize(self.w, self.h)

        self.timer.start()
        return
        

    def change_ralenti(self, ralenti):
        self.ralenti = ralenti
        self.label_2.setText(self.tr(
            "Ralenti : 1/{}".format(ralenti)))
        self.timer.setInterval(int(self.delay * self.ralenti))

    def toQimage(self, img):
        """Conversion image opencv en QPixmap"""
        rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        bytes_per_line = ch * w
        convert_to_Qt_format = QImage(
            rgb.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
        p = convert_to_Qt_format.scaled(self.w, self.h, Qt.AspectRatioMode.KeepAspectRatio)
        return QPixmap.fromImage(p)

    def affiche_image(self):
        image_suivante = next(self.images)
        p              = next(self.origines)
        hautgauche = (p + self.cadreur.decal -
                      self.cadreur.rayons) * self.ech
        taille = self.cadreur.sz * self.ech
        self.cadreur.capture.set(
            cv2.CAP_PROP_POS_FRAMES, image_suivante)
        status, img = self.cadreur.capture.read()
        img = self.cadreur.rotateImage(img, self.cadreur.video.rotation)
        w, h = int(taille.x), int(taille.y)
        x, y = int(hautgauche.x), int(hautgauche.y)

        crop_img = img[y:y+h, x:x+w]
        # NOTE: its img[y: y + h, x: x + w] and *not* img[x: x + w, y: y + h]
        self.label.setPixmap(self.toQimage(crop_img))
        return

class openCvReader:
    """
    Un lecteur de vidéos qui permet d'extraire les images une par une
    """

    def __init__(self, filename):
        """
        Le constructeur tente d'ouvrir le fichier video. En cas d'échec
        la valeur booléenne de l'instance sera False. Le test de validité est
        isolé dans un sous-shell
        @param filename le nom d'un fichier vidéo
        """
        self.filename = filename
        self.autoTest()
        self.index_precedent = 0
        self.cache = None # un cache pour l'image précédente
        if self.ok:
            self.capture = cv2.VideoCapture(self.filename)
        return

    def autoTest(self):
        #        if sys.platform == 'win32':
        import testfilm
        self.ok = testfilm.film(self.filename).ok
        return
    def __int__(self):
        return int(self.ok)

    def __nonzero__(self):
        return self.ok

    def getImage(self, index, angle=0, rgb=True):
        """
        récupère un array numpy
        @param index le numéro de l'image, commence à 1.
        @param angle 0, 90, 180 ou 270 : rotation de l'image (0 par défaut)
        @apame rgb (vrai par defaut) s'il est faux l'image est au format BGR
        @return le statut, l'image trouvée au format d'openCV
        """
        if self.capture:
            if self.cache is not None and index == self.index_precedent:
                img = self.cache
            else:
                if index != self.index_precedent+1:
                    # on ne force pas la position de lecture
                    # si on passe juste à l'image suivante
                    self.capture.set(cv2.CAP_PROP_POS_FRAMES, index-1)
                _, img = self.capture.read()
            # on cache l'image pour après
            self.cache = img
            # convertit dans le bon format de couleurs
            if rgb: img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            self.index_precedent = index
            return True, self.rotateImage(img, angle)
        else:
            return False, None

    def rotateImage(self, img, angle):
        if angle == 90:
            return cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
        elif angle == 270:
            return cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)
        elif angle == 180:
            return cv2.rotate(img, cv2.ROTATE_180)
        else:
            return img  # angle==0

    def recupere_avi_infos(self, angle=0):
        """
        Détermine les fps, le nombre de frames, la largeur, la hauteur d'un fichier vidéo
        @return un quadruplet (framerate,nombre d'images,la largeur, la hauteur)
        """
        try:
            fps = self.capture.get(cv2.CAP_PROP_FPS)
            fcount = self.capture.get(cv2.CAP_PROP_FRAME_COUNT)

            largeur = self.capture.get(cv2.CAP_PROP_FRAME_WIDTH)
            hauteur = self.capture.get(cv2.CAP_PROP_FRAME_HEIGHT)
            if angle % 180 == 90:  # la vidéo est tournée à droite ou à gauche
                largeur, hauteur = hauteur, largeur
        except:
            print("could not retrieve informations from the video file.")
            print("assuming fps = 25, frame count = 10.")
            return 25, 10, 320, 200
        return int(fps), int(fcount), int(largeur), int(hauteur)

    def __str__(self):
        return f"<openCvReader instance: filename={self.filename}>"


if __name__ == '__main__':
    if len(sys.argv) > 1:
        vidfile = sys.argv[1]
    else:
        vidfile = '/usr/share/python-mecavideo/video/g1.avi'
    cvReader = openCvReader(vidfile)
    if cvReader:
        print("Ouverture du fichier %s réussie" % vidfile)
    else:
        print("Ouverture manquée pour le fichier %s" % vidfile)
