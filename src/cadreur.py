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
from PyQt5.QtCore import QObject, QThread, pyqtSignal, QLocale, QTranslator, Qt, QSize, QTimer, QCoreApplication, QMetaObject
from PyQt5.QtGui import QKeySequence, QIcon, QPixmap, QImage
from PyQt5.QtWidgets import QVBoxLayout, QLabel, QSizePolicy, QFrame, QGridLayout, QSlider, QDialogButtonBox, QDialog
from vecteur import vecteur
from itertools import cycle


class Cadreur(QObject):
    """
    Un objet capable de recadrer une vidéo en suivant le déplacement
    d'un point donné. 
    Paramètres du constructeur :
    @param obj le numéro de l'objet qui doit rester immobile
    @param video le videoWidget où on a pointé les objets à suivre
    @param titre le titre désiré pour la fenêtre
    """

    def __init__(self, obj, video, titre=None):
        QObject.__init__(self)
        self.video = video
        if titre == None:
            self.titre = str(self.tr("Presser la touche ESC pour sortir"))
        self.obj = obj
        # on s'intéresse à la trajectoire de l'objet servant de référentiel
        self.trajectoire_obj = [video.data[t][obj] for t in video.dates
                                if self.video.data[t][obj]]
        # on fait la liste des index où l'objet a été pointé
        self.index_obj = [i for i,t in enumerate(video.dates)
                          if self.video.data[t][obj]]
        self.capture = cv2.VideoCapture(self.video.filename)
        self.fps = self.capture.get(cv2.CAP_PROP_FPS)
        self.delay = int(1000.0 / self.fps)
        self.video.dbg.p(2, "In : Video, self.obj %s" %
                       (self.obj))
        self.video.dbg.p(3, "In : Video, __init__, fps = %s and delay = %s" % (
            self.fps, self.delay))

        self.ralenti = 3
        self.fini = False
        self.maxcadre()

    def echelleTaille(self):
        """
        Renvoie l'échelle qui permet de passer de l'image dans pymecavideo
        à l'image effectivement trouvée dans le film, et la taille du film
        @return un triplet échelle, largeur, hauteur (de l'image dans le widget de de pymecavideo)
        """
        m = self.video.imageExtraite.size()
        echx = 1.0 * m.width() / self.video.width()
        echy = 1.0 * m.height() / self.video.height()
        ech = max(echx, echy)
        return ech, int(m.width() / ech), int(m.height() / ech)

    def controleRalenti(self, position):
        """
        fonction de rappel commandée par le bouton "Quitte"
        """
        self.ralenti = max([1, position])

    def maxcadre(self):
        """
        calcule le plus grand cadre qui peut suivre le point n° obj
        sans déborder du cadre de la vidéo. Initialise self.rayons qui indique
        la taille de ce cadre, et self.decal qui est le décalage du point
        à suivre par rapport au centre du cadre.
        """
        ech, w, h = self.echelleTaille()

        agauche = []
        dessus = []
        for p in self.trajectoire_obj:
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

    def montrefilm(self, fini=False):
        """
        Calcule et montre le film recadré à l'aide d'OpenCV
        """
        self.dialog = RalentiWidget(parentObject=self)
        self.dialog.exec_()

    def rotateImage(self, img, angle):
        if angle == 90:
            return cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
        elif angle == -90:
            return cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)
        elif angle == 180:
            return cv2.rotate(img, cv2.ROTATE_180)
        else:
            return img  # angle=0


class RalentiWidget(QDialog):

    """Affiche le film recadré"""

    def __init__(self, parentObject):
        super().__init__()
        self.cadreur = parentObject
        self.ralenti = 1
        self.images   = cycle(self.cadreur.index_obj)
        self.origines = cycle(self.cadreur.trajectoire_obj)
        self.delay = self.cadreur.delay
        self.ech, self.w, self.h = self.cadreur.echelleTaille()
        self.verticalLayout = QVBoxLayout(self)
        self.label_2 = QLabel(self)
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.label_2.sizePolicy().hasHeightForWidth())
        self.label_2.setSizePolicy(sizePolicy)
        self.label_2.setFrameShape(QFrame.Box)
        self.label_2.setAlignment(Qt.AlignCenter)
        self.label_2.setText("")
        self.verticalLayout.addWidget(self.label_2)
        self.gridLayout = QGridLayout()
        self.label = QLabel(self)
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        self.label.setMinimumSize(QSize(100, 0))
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.horizontalSlider = QSlider(self)
        self.horizontalSlider.setMinimum(1)
        self.horizontalSlider.setMaximum(16)
        self.horizontalSlider.setPageStep(4)
        self.horizontalSlider.setOrientation(Qt.Horizontal)
        self.gridLayout.addWidget(self.horizontalSlider, 0, 1, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout)
        self.buttonBox = QDialogButtonBox(self)
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Close)
        self.buttonBox.setCenterButtons(True)
        self.verticalLayout.addWidget(self.buttonBox)
        QMetaObject.connectSlotsByName(self)
        self._translate = QCoreApplication.translate
        self.retranslateUi()
        self.timer = QTimer()
        self.timer.setInterval(int(self.delay * self.ralenti))
        self.timer.timeout.connect(self.affiche_image)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        self.horizontalSlider.valueChanged.connect(self.change_ralenti)
        self.label_2.resize(self.w, self.h)
        self.timer.start()

    def retranslateUi(self):
        self.setWindowTitle(self._translate("MontreFilm", "Voir la vidéo"))
        self.label.setText(self._translate("MontreFilm", "Ralenti : 1/1"))

    def change_ralenti(self, ralenti):
        self.ralenti = ralenti
        self.label.setText(self._translate(
            "MontreFilm", "Ralenti : 1/{}".format(ralenti)))
        self.timer.setInterval(int(self.delay * self.ralenti))

    def toQimage(self, img):
        """Conversion image opencv en QPixmap"""
        rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        bytes_per_line = ch * w
        convert_to_Qt_format = QImage(
            rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
        p = convert_to_Qt_format.scaled(self.w, self.h, Qt.KeepAspectRatio)
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
        self.label_2.setPixmap(self.toQimage(crop_img))
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
        @param angle 0, 90, 18 ou -90 : rotation de l'image (0 par défaut)
        @apame rgb (vrai par defaut) s'il est faux l'image est au format BGR
        @return le statut, l'image trouvée
        """
        if self.capture:
            if index != self.index_precedent+1:
                # on ne force pas la position de lecture
                # si on passe juste à l'image suivante
                self.capture.set(cv2.CAP_PROP_POS_FRAMES, index-1)
            status, img = self.capture.read()
            self.index_precedent = index
            # convertit dans le bon format de couleurs
            if rgb:
                return True, self.rotateImage(
                    cv2.cvtColor(img, cv2.COLOR_BGR2RGB), angle)
            else:
                return True, self.rotateImage(
                    img, angle)
        else:
            return False, None

    def rotateImage(self, img, angle):
        if angle == 90:
            return cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
        elif angle == -90:
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
            if abs(angle) == 90:  # on a retourné la vidéo
                largeur, hauteur = hauteur, largeur
        except:
            print("could not retrieve informations from the video file.")
            print("assuming fps = 25, frame count = 10.")
            return 25, 10, 320, 200
        return int(fps), int(fcount), int(largeur), int(hauteur)

    def __str__(self):
        return "<openCvReader instance: filename=%s, nextImage=%d>" % (self.filename, self.nextImage)


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
