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

import cv2.cv as cv
import cv2
from PyQt4.QtCore import *
from PyQt4.QtGui import *

from vecteur import vecteur
from globdef import PYMECA_SHARE


class Cadreur(QObject):
    """
    Un objet capable de recadrer une vidéo en suivant le déplacement
    d'un point donné. La video de départ mesure 640x480
    """

    def __init__(self, numpoint, app, titre=None):
        QObject.__init__(app)
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

        self.capture = cv2.VideoCapture(self.app.filename.encode('utf8'))
        self.fps = self.capture.get(cv.CV_CAP_PROP_FPS)
        self.delay = int(1000.0 / self.fps)

        self.app.dbg.p(3, "In : Label_Video, __inti__, fps = %s and delay = %s" % (self.fps, self.delay))

        self.ralenti = 3
        self.fini = False
        self.maxcadre()


    def echelleTaille(self):
        """
        Renvoie l'échelle qui permet de passer de l'image dans pymecavideo
        à l'image effectivement trouvée dans le film, et la taille du film
        @return un triplet échelle, largeur, hauteur (de l'image dans le widget de de pymecavideo)
        """
        m = QImage(self.app.chemin_image).size()
        echx = 1.0 * m.width() / 640
        echy = 1.0 * m.height() / 480
        # permet de prendre en compte les vidéos à un format différent de 4:3
        ech = max(echx, echy)
        return ech, m.width() / ech, m.height() / ech


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

        agauche = [pp[self.numpoint].x() for pp in self.app.points.values()]
        dessus = [pp[self.numpoint].y() for pp in self.app.points.values()]
        adroite = [w - x - 1 for x in agauche]
        dessous = [h - y - 1 for y in dessus]

        agauche = min(agauche)
        adroite = min(adroite)
        dessus = min(dessus)
        dessous = min(dessous)
        self.tl = vecteur(agauche, dessus)  #topleft
        self.sz = vecteur(adroite + agauche, dessous + dessus)  #size

        self.decal = vecteur((adroite - agauche) / 2, (dessous - dessus) / 2)
        self.rayons = vecteur((agauche + adroite) / 2, (dessus + dessous) / 2)


    def queryFrame(self):
        """
        récupère l'image suivante du film et traite le cas où OpenCV
        ne sait pas le faire
        @return une IplImage
        """
        if cv.GrabFrame(self.capture):
            return cv.RetrieveFrame(self.capture)
        else:
            print "erreur, OpenCV 2.1 ne sait pas extraire des images du fichier", videofile
            sys.exit(1)


    def montrefilm(self, fini=False):
        """
        Calcule et montre le film recadré à l'aide d'OpenCV
        """
        wsub = cv.NamedWindow(self.titre)

        ralentiLabel = "Choisir le ralenti"

        cv.CreateTrackbar(ralentiLabel, self.titre, 0, 16, self.controleRalenti)
        ech, w, h = self.echelleTaille()
        i = 0
        while not fini:


            #rembobine
            self.capture = cv.CreateFileCapture(self.app.filename.encode('utf8'))

            #have to move to first picture clicked

            cv.SetCaptureProperty(self.capture, cv.CV_CAP_PROP_POS_FRAMES, self.app.premiere_image - 1)

            for i in self.app.points.keys():
                p = self.app.points[i][self.numpoint]
                hautgauche = (p + self.decal - self.rayons) * ech
                taille = self.sz * ech
                img = self.queryFrame()

                x, y = int(hautgauche.x()), int(hautgauche.y())
                w, h = int(taille.x()), int(taille.y())
                isub = cv.GetSubRect(img, (x, y, w, h))
                cv.ShowImage(self.titre, isub)
                k = cv.WaitKey(int(self.delay * self.ralenti))
                if k == 0x10001b or k == 27:
                    fini = True
                    cv.DestroyAllWindows()
                    break

        cv.DestroyWindow(self.titre)
        fini = True


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
        self.rembobine()

    def autoTest(self):
        #        if sys.platform == 'win32':
        import testfilm
        self.ok = testfilm.film(self.filename).ok

    def __int__(self):
        return int(self.ok)

    def __nonzero__(self):
        return self.ok

    def rembobine(self):
        """
        Recharge le fichier vidéo
        """

        try:
            self.filename = unicode(self.filename, 'utf8')
        except TypeError:
            pass
        self.capture = cv.CreateFileCapture(self.filename.encode('utf8'))
        self.nextImage = 1


    def getImage(self, index):
        """
        récupère une IplImage
        @param index le numéro de l'image, commence à 1.
        @return l'image trouvée
        """
        if index < self.nextImage:
            self.rembobine()
        while index >= self.nextImage:
            if cv.GrabFrame(self.capture):
                img = cv.RetrieveFrame(self.capture)
                self.nextImage += 1
            else:
                return None
        return img

    def writeImage(self, index, imgFileName):
        """
        Enregistre une image de la vidéo
        @param index le numéro de l'image (commence à 1)
        @param imgFileName un nom de fichier pour l'enregistrement
        @return vrai si l'enregistrement a réussi
        """
        img = self.getImage(index)
        if img:
            cv.SaveImage(imgFileName, img)
            return True
        else:
            return False

    def recupere_avi_infos(self):
        """
        Détermine les fps, le nombre de frames, la largeur, la hauteur d'un fichier vidéo
        @return un quadruplet (framerate,nombre d'images,la largeur, la hauteur)
        """
        try:
            self.rembobine()
            fps = cv.GetCaptureProperty(self.capture, cv.CV_CAP_PROP_FPS)
            fcount = cv.GetCaptureProperty(self.capture, cv.CV_CAP_PROP_FRAME_COUNT)
            largeur = cv.GetCaptureProperty(self.capture, cv.CV_CAP_PROP_FRAME_WIDTH)
            hauteur = cv.GetCaptureProperty(self.capture, cv.CV_CAP_PROP_FRAME_HEIGHT)
        except:
            print "could not retrieve informations from the video file."
            print "assuming fps = 25, frame count = 10."
            return 25, 10, 320, 200
#        return fps, fcount
        return fps, fcount - 1, largeur, hauteur

    def __str__(self):
        return "<openCvReader instance: filename=%s, nextImage=%d>" % (self.filename, self.nextImage)


if __name__ == '__main__':
    if len(sys.argv) > 1:
        vidfile = sys.argv[1]
    else:
        vidfile = '/usr/share/python-mecavideo/video/g1.avi'
    cvReader = openCvReader(vidfile)
    if cvReader:
        print "Ouverture du fichier %s réussie" % vidfile
    else:
        print "Ouverture manquée pour le fichier %s" % vidfile
