#-*- coding: utf-8 -*-

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

import sys, os#, thread, time, commands
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from math import sqrt, acos, asin, pi, cos, sin, atan2
from vecteur import vecteur
import re, subprocess, shutil
from globdef import AVI_OUT, GetChildStdErr ,CROP, IMG_PATH

class Cadreur:
    def __init__(self,numpoint,app):
        """
        Crée un objet capable de recadrer une vidéo en suivant le déplacement
        d'un point donné. La video de départ mesure 640x480
        """
        self.numpoint=numpoint
        self.app=app
        self.maxcadre()

    def maxcadre(self):
        """
        calcule le plus grand cadre qui peut suivre le point n° numpoint
        sans déborder du cadre de la vidéo. Initialise self.rayons qui indique
        la taille de ce cadre, et self.decal qui est le décalage du point
        à suivre par rapport au centre du cadre.
        """
        dessus=480; dessous=480
        agauche=640; adroite=640
        for i in self.app.points.keys():
            p=self.app.points[i][self.numpoint]
            x=p.x(); y=p.y() # attention : axe y dirigé vers le bas
            if x < agauche: agauche=x
            if 640-x < adroite: adroite=640-x
            if y < dessus: dessus=y
            if 480-y < dessous: dessous=480-y
        self.decal=vecteur((adroite-agauche)/2, (dessous-dessus)/2)
        self.rayons=vecteur((agauche+adroite)/2, (dessus+dessous)/2)
            

    def cropimages(self):
        """
        crée une nouvelle série d'images en découpant dans la vidéo de
        départ.
        """
        
        #regexp_taille=re.compile(".*[^1-9]([1-9][0-9]*) x ([1-9][0-9]*).*")
        #st,out = commands.getstatusoutput("file -L %s" %self.app.filename)
        #m=regexp_taille.match(out)
        #if not m : return
        m = QImage(self.app.chemin_image).size()
        self.taille=vecteur(m.width(),m.height())
        ech=self.taille.norme()/vecteur(640,480).norme()
        
        if sys.platform == 'win32':
            liste_fichier = os.listdir(IMG_PATH)
            for fichier in liste_fichier :
                if CROP in fichier:
                    os.remove(os.path.join(IMG_PATH, fichier))
        else:
            os.chdir(self.app._dir("images"))
            liste_fichier = os.listdir(".")
            for fichier in liste_fichier :
                if CROP in fichier:
                    os.remove(fichier)
        for i in self.app.points.keys():
            p=self.app.points[i][self.numpoint]
            # calcule les vecteurs des marges
            hautgauche=(p+self.decal-self.rayons)*ech
            basdroite=(vecteur(640,480)-(p+self.decal+self.rayons))*ech
            hautgauche.rounded()
            basdroite.rounded()
            ## les bandes en haut et en bas doivent avoir
            ## un nombre pair de lignes
            if hautgauche.x()%2==1 : hautgauche += vecteur(1,0)
            if basdroite.x()%2==1  : basdroite  += vecteur(1,0)
            if hautgauche.y()%2==1 : hautgauche += vecteur(0,1)
            if basdroite.y()%2==1  : basdroite  += vecteur(0,1)
            cmd = [self.app.ffmpeg, """-i""", self.app.filename, """-ss""", str((i+self.app.premiere_image-1) *self.app.deltaT),
                   """-vframes""", """1""", """-f""", """image2""", """-vcodec""", """mjpeg""", 
                   """-cropleft""",  str(hautgauche.x()) , """-croptop""",    str(hautgauche.y())  , 
                   """-cropright""", str(basdroite.x())  , """-cropbottom""", str(basdroite.y()) ]
           
            if sys.platform == 'win32':
                cmd.append(os.path.join(IMG_PATH, CROP + "%04d.jpg" %i))
            else:
                cmd.append(CROP + "%04d.jpg" %i)
            
            childstderr, creationflags = GetChildStdErr()
            crop = subprocess.Popen(cmd, #shell=True, 
                                    stderr = subprocess.PIPE, stdin = childstderr, stdout = childstderr,
                                    creationflags = creationflags )
            crop.wait()
            
            
        
    def creefilm(self, ralenti):
        i=0
        for j in self.app.points.keys():
            for k in range(ralenti):
                # reproduit "ralenti" fois les trames
                #print i,j
                fichier1 = os.path.join(IMG_PATH, CROP + "%04d.jpg" % j) 
                fichier2 = os.path.join(IMG_PATH, CROP +"-%04d.jpg" % i)
                shutil.copy(fichier1,fichier2)
                i+=1
        try :
            os.remove(AVI_OUT)
        except OSError :
            pass
        
        if sys.platform == 'win32':
            cropfile = os.path.join(IMG_PATH, CROP+"-%04d.jpg")
        else:
            cropfile = CROP+"-%04d.jpg"
        
        cmd = [self.app.ffmpeg, """-r""", """25""", """-f""", """image2""", """-i""", cropfile,
               """-r""", """25""", """-f""", """avi""", """-vcodec""", """mpeg1video""", 
               """-b""", """800k""", AVI_OUT]
        
        print "film", AVI_OUT, cmd
        childstderr, creationflags = GetChildStdErr()
        crop = subprocess.Popen(cmd, #shell=True, 
                                stderr = subprocess.PIPE, stdin = childstderr, stdout = childstderr,
                                creationflags = creationflags)
        crop.wait()
        print crop.returncode
        
        
    def montrefilm(self):
        #print self.app.prefs.videoPlayerCmd()
        print self.app.player
    
        #self.app.dbg.p(2,"%s" %(cmd))
        childstderr, creationflags = GetChildStdErr()
        montre = subprocess.Popen(self.app.player + [AVI_OUT], 
                                  stderr = subprocess.PIPE, stdin = childstderr, stdout = childstderr,
                                  creationflags = creationflags)
        montre.wait()
