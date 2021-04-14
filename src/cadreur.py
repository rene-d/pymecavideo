# -*- coding: utf-8 -*-

"""
    cadreur, a module for pymecavideo:
      a program to track moving points in a video frameset
      
    Copyright (C) 2007 Jean-Baptiste Butet <ashashiwa@gmail.com>

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
    d'un point donné. La video de départ mesure 640x480
    """

    def __init__(self, numpoint, app, titre=None):
        """
        Le constructeur.
        @param numpoint le numéro du point qui doit rester immobile
        @param app l'application Pymecavideo
        @param titre le titre désiré pour la fenêtre
        """
        self.app = app
        self.app.dbg.p(1, "In : Cadreur, __init__")
        if titre == None:
            self.titre = str(self.app.tr("Presser la touche ESC pour sortir"))

        self.numpoint = numpoint
        self.app = app

        self.capture = cv2.VideoCapture(
            str(self.app.filename.encode('utf8'), 'utf8'))
        self.fps = self.capture.get(cv2.CAP_PROP_FPS)
        self.delay = int(1000.0 / self.fps)
        self.app.dbg.p(2, "In : Label_Video, self.numpoint %s" %
                       (self.numpoint))
        self.app.dbg.p(3, "In : Label_Video, __init__, fps = %s and delay = %s" % (
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
        m = self.app.imageExtraite.size()
        echx = 1.0 * m.width() / self.app.label_video.width()
        echy = 1.0 * m.height() / self.app.label_video.height()
        ech = max(echx, echy)
        return ech, int(m.width() / ech), int(m.height() / ech)

    def controleRalenti(self, position):
        """
        fonction de rappel commandée par le bouton "Quitte"
        """
        self.ralenti = max([1, position])

    def maxcadre(self):
        """
        calcule le plus grand cadre qui peut suivre le point n° numpoint
        sans déborder du cadre de la vidéo. Initialise self.rayons qui indique
        la taille de ce cadre, et self.decal qui est le décalage du point
        à suivre par rapport au centre du cadre.
        """
        ech, w, h = self.echelleTaille()

        # agauche = [pp[self.numpoint].x() for pp in self.app.points.values()]  #ne gère pas les excemtion si il manqu eun point
        #dessus = [pp[self.numpoint].y() for pp in self.app.points.values()]

        agauche = []
        dessus = []
        for pp in self.app.points.values():
            try:
                agauche.append(pp[self.numpoint].x())
                dessus.append(pp[self.numpoint].y())
            except:
                pass  # si il manque des points dans la dernière image)

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

        # cv2.namedWindow(self.titre)

        #ralentiLabel = str(self.app.tr("Choisir le ralenti"))

        #cv2.createTrackbar(ralentiLabel, self.titre, 0, 16, self.controleRalenti)
        #ech, w, h = self.echelleTaille()
        #self.capture = cv2.VideoCapture(str(self.app.filename.encode('utf8'), 'utf8'))
        # while not fini:
        # for i in self.app.points.keys():
        # try :
        #p = self.app.points[i][self.numpoint]
        #hautgauche = (p + self.decal - self.rayons) * ech
        #taille = self.sz * ech
        #self.capture.set(cv2.CAP_PROP_POS_FRAMES, i + self.app.premiere_image)
        #status, img =  self.capture.read()
        #img = self.rotateImage(img, self.app.rotation)
        #w, h = int(taille.x()), int(taille.y())
        #x, y = int(hautgauche.x()), int(hautgauche.y())

        # crop_img = img[y:y+h, x:x+w] # Crop from x, y, w, h -> 100, 200, 300, 400
        # NOTE: its img[y: y + h, x: x + w] and *not* img[x: x + w, y: y + h]
        #cv2.imshow(self.titre, crop_img)
        #k = cv2.waitKey(int(self.delay * self.ralenti))
        # if k == 0x10001b or k == 27 or k==20:
        #fini = True
        # cv2.destroyAllWindows()
        # break
        # except : pass #si pas le bon nombre de points dans la dernière image

        # cv2.destroyAllWindows()
        #fini = True
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
        self.images = cycle(self.cadreur.app.points.keys())
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
        try:
            p = self.cadreur.app.points[image_suivante][self.cadreur.numpoint]
            hautgauche = (p + self.cadreur.decal -
                          self.cadreur.rayons) * self.ech
            taille = self.cadreur.sz * self.ech
            self.cadreur.capture.set(
                cv2.CAP_PROP_POS_FRAMES, image_suivante + self.cadreur.app.premiere_image)
            status, img = self.cadreur.capture.read()
            img = self.cadreur.rotateImage(img, self.cadreur.app.rotation)
            w, h = int(taille.x()), int(taille.y())
            x, y = int(hautgauche.x()), int(hautgauche.y())

            # Crop from x, y, w, h -> 100, 200, 300, 400
            crop_img = img[y:y+h, x:x+w]
            # NOTE: its img[y: y + h, x: x + w] and *not* img[x: x + w, y: y + h]
            self.label_2.setPixmap(self.toQimage(crop_img))
        except:
            pass


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

    def autoTest(self):
        #        if sys.platform == 'win32':
        import testfilm
        self.ok = testfilm.film(self.filename).ok

    def __int__(self):
        return int(self.ok)

    def __nonzero__(self):
        return self.ok

    def getImage(self, index, angle):
        """
        récupère un array numpy
        @param index le numéro de l'image, commence à 1.
        @return le statut, l'image trouvée
        """
        temps0 = time.time()
        if self.capture:
            if index != self.index_precedent+1:
                self.capture.set(cv2.CAP_PROP_POS_FRAMES, index-1)
            try:
                status, img = self.capture.read()
                self.index_precedent = index
            except cv2.error:
                print("Erreur, image non décodée")
                return False, None
            except Exception as err:
                print("Erreur :", err)
                return False, None
            # convertit dans le bon format de couleurs
            img2 = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        else:
            return False, None

        return True, self.rotateImage(img2, angle)

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
#        return fps, fcount
        return fps, fcount, int(largeur), int(hauteur)

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
