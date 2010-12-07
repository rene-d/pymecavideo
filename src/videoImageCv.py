# -*- coding: utf-8 -*-

licence={}
licence['en']="""
    pymecavideo version %s:

    a program to track moving points in a video frameset
    
    Copyright (C) 2007-2008 Jean-Baptiste Butet <ashashiwa@gmail.com>
    
    Copyright (C) 2007-2008 Georges Khaznadar <georgesk@ofset.org>

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

licence['fr']=u"""
    pymecavideo version %s :

    un programme pour tracer les trajectoires des points dans une vidéo.
    
    Copyright (C) 2007-2008 Jean-Baptiste Butet <ashashiwa@gmail.com>
    
    Copyright (C) 2007-2008 Georges Khaznadar <georgesk@ofset.org>
    
    Ce projet est un logiciel libre : vous pouvez le redistribuer, le modifier selon les terme de la GPL (GNU Public License) dans les termes de la Free Software Foundation concernant la version 3 ou plus de la dite licence.
    
    Ce programme est fait avec l'espoir qu'il sera utile mais SANS AUCUNE GARANTIE. Lisez la licence pour plus de détails.
    
    <http://www.gnu.org/licenses/>.
"""

from PyQt4.QtGui import QApplication,QMessageBox

from globdef import PATH, IMG_PATH, VIDEO, SUFF, GetChildStdErr

import os.path, subprocess, re, platform

import cv
from cv import *

class film:
    """
    Une classe pour accéder aux images d'un film
    """
    def __init__(self,filename):
        """
        le constructeur
        @param filename le nom d'un fichier video
        """
        self.filename="%s" %filename.encode()
        self.capture = CreateFileCapture(self.filename)
        self.frame=QueryFrame(self.capture)
        self.num=0
        self.fps=GetCaptureProperty(self.capture,CV_CAP_PROP_FPS)
        self.framecount=GetCaptureProperty(self.capture,CV_CAP_PROP_FRAME_COUNT)
        
    def image(self,num,recode=None):
        """
        accès à une image du film, avec rembobinage du film si nécessaire
        @param num l'image recherchée
        @param recode recodage si nécessaire, peut valoir 'PIL'. None par défaut
        @return un objet de type IplImage ou None si la fin du film est dépassée
        """
        if num>self.num:
            for i in range(self.num,num):
                self.frame=QueryFrame(self.capture)
        elif 0<=num<self.num: 
            #ReleaseCapture(self.capture)
            self.capture = CreateFileCapture(self.filename)
            for i in range (0, num+1):
                self.frame=QueryFrame(self.capture)
        self.num=num
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
        
class videoImage:
    """
    Une classe pour la gestion des images que contient une vidéo
    """

    def __init__(self, videoFileName=None):
        """
        Le constructeur
        """
        if videoFileName == None:
            self.videoFileName=None
            self.film=None
            self.framerate = 25      # vitesse des vidéos pas défaut
            self.deltaT = 0.04       # durée 40 ms par défaut : 25 images/s
            self.image_max=None
        else:
            self.initFromFile(videoFileName)
        self.chemin_image=None
        self.ffmpeg = None       # on ignore le nom de la commande au début
        self.platform = None     # de même on ignore la plateforme.

        self.initPlatform()

    def initFromFile(self,videoFileName):
        """
        Initialisations depuis un nom de fichier vidéo
        """
        self.videoFileName=videoFileName
        self.film=film(videoFileName)
        self.framerate=self.film.tramesParSeconde()
        self.deltaT=1.0/self.framerate
        self.image_max=self.film.totalTrames()-1
        for i in range(self.image_max+1):
            self.extract_image(i,force=True)
        

    def initPlatform(self):
        """
        Réalise le initialisations spécifiques à la plateforme
        """
        self.platform = platform.system()
        if self.platform.lower()=="windows":
            self.ffmpeg = os.path.join(PATH,"ffmpeg.exe")
            self.player = "ffplay.exe"

        elif self.platform.lower()=="linux":
            self.ffmpeg = "ffmpeg"
            self.player = "vlc"
        ######vérification de la présence de fmmpeg et ffplay dans le path.
        ok_ffmpeg=True; ok_player=True;
        if self.platform == 'windows':
            paths = os.environ['PATH'].split(os.pathsep)
            paths.append(PATH)
            if not( any(os.access(os.path.join(p,self.ffmpeg), os.X_OK) for p in paths)) :
                ok_ffmpeg = False
        else:
            if type(self.player)==type([]):
                player=self.player[0]
            else:
                player=self.player.split(" ")[0]
            # on garde le nom de commande, pas les paramètres
            if not( any(os.access(os.path.join(p,self.ffmpeg), os.X_OK) for p in os.environ['PATH'].split(os.pathsep))) :
                ok_ffmpeg = False
            if not(any(os.access(os.path.join(p,player), os.X_OK) for p in os.environ['PATH'].split(os.pathsep))) :
                ok_player = False
        if ok_player== False or ok_ffmpeg == False :
            pas_ffmpeg = QMessageBox.warning(self,self.tr(unicode("ERREUR !!!","utf8")),QString(self.tr(unicode("le logiciel %s ou %s n'a pas été trouvé sur votre système. Merci de bien vouloir l'installer avant de poursuivre" %(self.ffmpeg, player),"utf8" ))), QMessageBox.Ok,QMessageBox.Ok)
            #self.close()

    def extract_image(self, index, force=False):
        """
        extrait l'image d'index "index" de la video à l'aide de ffmpeg
        et l'enregistre sur le disque.
        @param index désigne l'image
        @param force booléen pour forcer la réécriture d'une image même si elle existe déjà
        """
        imfilename=os.path.join(IMG_PATH, VIDEO + SUFF %index).encode()
        self.chemin_image = imfilename
        if not os.path.isfile(imfilename) or force==True:
            if self.film == None:
                self.initFromFile(self.videoFileName)
            img=self.film.image(index-1)
            if img: SaveImage(imfilename,img)

          
    def videoCropCmd(self, image, hautgauche, basdroite):
        """
        compose et renvoie une commande servent à faire un extrait de video
        @param image numéro de l'image à découper
        @param hautgauche coordonnées d'un coin de la zone à découper
        @param basdroite coordonnées de l'autre coin
        @return une commande pour découper un rectangle dans une image de la vidéo
        """
        cmd = [self.ffmpeg,
               """-i""", self.videoFileName,
               """-ss""", str(image *self.deltaT),
               """-vframes""", """1""",
               """-f""", """image2""",
               """-vcodec""", """mjpeg""", 
               """-cropleft""",  str(hautgauche.x()) ,
               """-croptop""",    str(hautgauche.y())  , 
               """-cropright""", str(basdroite.x())  ,
               """-cropbottom""", str(basdroite.y()) ]
        return cmd

    def videoMergeCmd(self, images, destfile):
        """
        renvoie une commande pour combiner une série d'images en une vidéo
        @param images désignation des images à monter en animation
        @param destfile fichier vidéo à créer
        """
        cmd = [self.ffmpeg,
               """-r""", """25""",
               """-f""", """image2""",
               """-i""", images,
               """-r""", """25""",
               """-f""", """avi""",
               """-vcodec""", """mpeg1video""", 
               """-b""", """800k""", destfile]
        return cmd
