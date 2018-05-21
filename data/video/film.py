#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function

import cv
import sys, threading


class film:
    """
    Une classe pour accéder aux images d'un film
    """

    def __init__(self, filename):
        """
        le constructeur
        @param filename le nom d'un fichier video
        """
        self.filename = filename

        self.capture = cv.CreateFileCapture(self.filename)
        t = threading.Thread(target=self.autoTest)
        t.start()
        t.join(5.0)  # attente de 5 secondes au plus


    def autoTest(self):
        self.ok = False
        try:
            self.frame = cv.QueryFrame(self.capture)
            self.num = 0
            self.fps = cv.GetCaptureProperty(self.capture, cv.CV_CAP_PROP_FPS)
            self.framecount = cv.GetCaptureProperty(self.capture, cv.CV_CAP_PROP_FRAME_COUNT)
            assert 1.0 * self.filesize / self.framecount > 2000, "fichier aberrant en taille"
            # plus de 200 octets par trame
            self.ok = True
        except:
            pass

    def __int__(self):
        return int(self.ok)

    def __nonzero__(self):
        return self.ok

    def image(self, num, recode=None):
        """
        accès à une image du film, avec rembobinage du film si nécessaire
        @param num l'image recherchée
        @param recode recodage si nécessaire, peut valoir 'PIL'. None par défaut
        @return un objet de type IplImage ou None si la fin du film est dépassée
        """
        if num > self.num:
            for i in range(self.num, num):
                self.frame = cv.QueryFrame(self.capture)
        elif 0 <= num < self.num:
            # cv.ReleaseCapture(self.capture)
            self.capture = cv.CreateFileCapture(self.filename)
            for i in range(0, num + 1):
                self.frame = cv.QueryFrame(self.capture)
        self.num = num
        if recode == 'PIL':
            return Ipl2PIL(self.frame)
        else:
            return self.frame

    def nbTrames(self):
        """
        @return Le nombre de trames du film
        """
        return int(self.framecount)

    def tramesParSeconde(self):
        """
        @return le nombre de trames par seconde
        """
        return int(self.fps)

    def totalTrames(self):
        """
        @return le nombre total de trames dans le film
        """
        return int(self.framecount)


##################### ci-dessous, des fonctions de démonstration seulement #####

import os.path, re


def showSlowAVI(fname):
    f = film(fname)
    if f:
        print ("vidéo : %s %d trames %d trames par seconde" % (fname, f.nbTrames(), f.tramesParSeconde()))
        loop = True
        forward = None
        num = 0
        frame = f.image(num)
        while (loop):
            if forward == True:
                num += 1
                frame = f.image(num)
            elif forward == False and num > 0:
                num -= 1
                frame = f.image(num)
            forward = None
            if (frame == None):
                break;
            cv.ShowImage("Example2", frame)
            char = cv.WaitKey(33)
            if (char != -1):
                if char == 1048603:  # ESC
                    loop = False
                elif char == 1048678:  # f
                    forward = True
                elif char == 1048674:  # b
                    forward = False
    else:
        print ("la vidéo %s n'est pas bien acceptée par OpenCV" % fname)
    cv.DestroyWindow("Example2")


def showMovies(arg, dirname, names):
    aviPattern = re.compile(".*\.avi$|.*\.mov$", re.I)
    for f in names:
        if aviPattern.match(f):
            showSlowAVI(os.path.join(dirname, f))


if __name__ == '__main__':
    if len(sys.argv) > 1:
        basedir = sys.argv[1]
    else:
        basedir = '/usr/share/python-mecavideo/video'
    print ("forward='f' backward='b' next='Esc'")
    cv.NamedWindow("Example2", cv.CV_WINDOW_AUTOSIZE)
    os.path.walk(basedir, showMovies, None)
    cv.DestroyWindow("Example2")
