#-*- coding: utf-8 -*-

"""
    cadreur, a module for pymecavideo:
      a program to track moving points in a video frameset
      
    Copyright (C) 2011 Georges Khaznadar <georgesk@ofset.org>

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

import sys, os, cv, time
import re, shutil
from threading import Thread
from subprocess import call
from os import mkfifo

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from vecteur import vecteur
from globdef import PYMECA_SHARE

class OpenCvContainer(QX11EmbedContainer):
    """
    Une classe spécialisée pour envelopper une fenêtre d'affichage d'OpenCv
    créée grâce à la commande "cadreur". Cette classe traite quelques messages
    qu'elle formate et transmet à la commande "cadreur" qu'elle enveloppe.
    """

    def __init__(self, parent=None, videofile="", fifoname=""):
        """
        Crée le conteneur Qt et y installe la fenêtre de la petite
        application cadreur.
        @param parent la fenêtre parente de ce conteneur
        @param videofile le nom d'un fichier vidéo à ouvrir
        @param fifoname le nom d'un tube par où communiquer avec l'application cadreur
        """
        QX11EmbedContainer.__init__(self, parent)
        self.videofile=videofile
        if os.path.exists(fifoname):
            os.unlink(fifoname)
            ## il faudrait peut-être plutôt stopper là et signaler
            ## qu'une autre instance de pymecavideo est déjà active ?
            ## ou alors créer un fichier temporaire unique.
        self.fifoname=fifoname
        os.mkfifo(fifoname)
        t0=Thread(target=self.fifoWriter, name="fifoThread")
        t0.start()
        t1=Thread(target=self.cadreur, name="cadreurThread")
        t1.start()

    def fifoWriter(self):
        self.fifoIn=open(self.fifoname,"w")
        sel.fifoIn.write("\n"); ## pour amorcer le fifo
        # on ne veut pas que le fifo soit bloquant à l'ouverture
        # pour le processus cadreur
        
    def cadreur(self):
        """
        Sert à lancer un commande dans un thread
        """
        cmd = "cadreur %s %s" %(self.videofile, self.fifoname)
        call(cmd, shell=True)

    def closeEvent(self,event):
        """
        Un crochet pour y mettre toutes les procédures à faire lors
        de la fermeture du widget. Envoie une commande de fermeture
        à l'application enrobée.
        """
        self.fifoIn.write("stop\n")
        event.accept()

class Cadreur:
    """
    Un objet capable de recadrer une vidéo en suivant le déplacement
    d'un point donné. La video de départ mesure 640x480
    """
    def __init__(self,numpoint,app, titre=None):
        """
        Le constructeur.
        @param numpoint le numéro du point qui doit rester immobile
        @param app l'application Pymecavideo
        @param titre le titre désiré pour la fenêtre
        """
        if titre==None:
            self.titre="Nouveau cadre"
        quitteLabel="Curseur à droite pour quitter"
        ralentiLabel="Choisir le ralenti"
        self.numpoint=numpoint
        self.app=app
        self.capture=cv.CreateFileCapture(self.app.filename)
        self.fps=cv.GetCaptureProperty(self.capture,cv.CV_CAP_PROP_FPS)
        self.delay=int(1000.0/self.fps)
        self.ralenti=1
        wsub=cv.NamedWindow(self.titre)
        cv.CreateTrackbar(quitteLabel,self.titre, 0, 1, self.controleStop)
        cv.CreateTrackbar(ralentiLabel,self.titre, 0, 16, self.controleRalenti)
        self.maxcadre()

    def controleStop(self,position):
        """
        fonction de rappel commandée par le bouton "Quitte"
        """
        if position==1:
            self.fini=True
            
    def controleRalenti(self,position):
        """
        fonction de rappel commandée par le bouton "Quitte"
        """
        self.ralenti=max([1,position])

    def maxcadre(self):
        """
        calcule le plus grand cadre qui peut suivre le point n° numpoint
        sans déborder du cadre de la vidéo. Initialise self.rayons qui indique
        la taille de ce cadre, et self.decal qui est le décalage du point
        à suivre par rapport au centre du cadre.
        """
        agauche=[pp[self.numpoint].x() for pp in self.app.points.values()]
        dessus=[pp[self.numpoint].y() for pp in self.app.points.values()]
        adroite=[640-x for x in agauche]
        dessous=[480-y for y in dessus]
        
        agauche=min(agauche)
        adroite=min(adroite)
        dessus=min(dessus)
        dessous=min(dessous)

        self.decal=vecteur((adroite-agauche)/2, (dessous-dessus)/2)
        self.rayons=vecteur((agauche+adroite)/2, (dessus+dessous)/2)
           

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
        
    def montrefilm(self):
        """
        Calcule et montre le film recadré à l'aide d'OpenCV
        """
        m = QImage(self.app.chemin_image).size()
        self.taille=vecteur(m.width(),m.height())
        ech=self.taille.norme()/vecteur(640,480).norme()
        
        self.fini=False
        while not self.fini:
            #rembobine
            self.capture=cv.CreateFileCapture(self.app.filename)
            for i in self.app.points.keys():
                if self.fini: break # valeur volatile à examiner souvent
                p=self.app.points[i][self.numpoint]
                hautgauche=(p+self.decal-self.rayons)*ech
                taille=self.rayons*2*ech
                img=self.queryFrame()
                x,y = int(hautgauche.x()), int(hautgauche.y())
                w,h = int(taille.x()), int(taille.y())
                isub = cv.GetSubRect(img, (x,y,w,h))
                cv.ShowImage(self.titre,isub)
                cv.WaitKey(self.delay*self.ralenti)
        # ferme la fenêtre
        cv.DestroyWindow(self.titre)

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
        self.filename=filename
        self.autoTest()
        self.rembobine()
        
    def autoTest(self):
        cmd="python %s %s" %(os.path.join(PYMECA_SHARE, 'testfilm.py'),
                             self.filename)
        retcode=call(cmd, shell=True)
        self.ok = retcode==0

    def __int__(self):
        return int(self.ok)
    def __nonzero__(self):
        return self.ok

    def rembobine(self):
        """
        Recharge le fichier vidéo
        """
        self.capture=cv.CreateFileCapture(self.filename)
        self.nextImage=1
        

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
                img=cv.RetrieveFrame(self.capture)
                self.nextImage+=1
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
        img=self.getImage(index)
        if img:
            cv.SaveImage(imgFileName, img)
            return True
        else:
            return False

    def recupere_avi_infos(self):
        """
        Trouve deux renseignements au sujet d'un fichier vidéo
        @return une paire (framerate,nombre d'images)
        """
        try:
            self.rembobine()
            fps=cv.GetCaptureProperty(self.capture,cv.CV_CAP_PROP_FPS)
            fcount=cv.GetCaptureProperty(self.capture,cv.CV_CAP_PROP_FRAME_COUNT)
        except:
            print "could not retrieve informations from the video file."
            print "assuming fps = 25, frame count = 10."
            return 25,10 
        return fps, fcount-1

    def __str__(self):
        return "<openCvReader instance: filename=%s, nextImage=%d>" %(self.filename, self.nextImage)


if __name__ == '__main__':
    if len(sys.argv)>1:
        vidfile=sys.argv[1]
    else:
        vidfile='/usr/share/python-mecavideo/video/g1.avi'
    cvReader=openCvReader(vidfile)
    if cvReader:
        print "Ouverture du fichier %s réussie" %vidfile
    else:
        print "Ouverture manquée pour le fichier %s"  %vidfile
