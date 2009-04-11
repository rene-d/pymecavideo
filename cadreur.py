#-*- coding: utf-8 -*-

"""
    cadreur, a module for pymecavideo:
      a program to track moving points in a video frameset
      
    Copyright (C) 2007 Jean-Baptiste Butet <ashashiwa@gmail.com>

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 2 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import sys, os, thread, time, commands
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from math import sqrt, acos, asin, pi, cos, sin, atan2
from vecteur import vecteur
import re

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
        #création du dictionnaire self.points

        self.points={}
        for key in self.app.points_ecran:
            self.points[key[0]] = []

        for key in self.app.points_ecran:
            self.points[key[0]] = self.points[key[0]]+ [self.app.points_ecran[key][3]]
            
        #self.points a pour structure : self.points {1: [vecteur (193.000000, 392.000000), vecteur (63.000000, 102.000000)]
        
       
        for i in self.points.keys():
            p=self.points[i][self.numpoint-1]
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
        
        regexp_taille=re.compile(".*[^1-9]([1-9][0-9]*) x ([1-9][0-9]*).*")
        st,out = commands.getstatusoutput("file -L %s" %self.app.filename)
        m=regexp_taille.match(out)
        print m
        if not m : return
        self.taille=vecteur(m.group(1),m.group(2))
        ech=self.taille.norme()/vecteur(640,480).norme()
        
        os.chdir(self.app._dir("images"))
        os.system("rm -f crop*.jpg")
        for i in self.points.keys():
            p=self.points[i][self.numpoint-1]
           
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
            cmd="ffmpeg -i %s -ss %f -vframes 1 -f image2 -vcodec mjpeg -cropleft %d -croptop %d -cropright %d -cropbottom %d crop%04d.jpg" %(self.app.filename,(i+self.app.premiere_image-1)*self.app.deltaT,hautgauche.x(),hautgauche.y(),basdroite.x(),basdroite.y(),i)
            st,out = commands.getstatusoutput(cmd)
            
        
    def creefilm(self, ralenti):
        i=0
        for j in self.points.keys():
            for k in range(ralenti):
                # reproduit "ralenti" fois les trames
                os.system("cp crop%04d.jpg crop-%04d.jpg" %(j,i))
                i+=1
        
        cmd= "rm -f out.avi; ffmpeg -r 25 -f image2 -i crop-%04d.jpg -r 25 -f avi -vcodec mpeg1video -b 800k out.avi"
        commands.getstatusoutput(cmd)

    def montrefilm(self):
        file="out.avi"
        cmd=self.app.prefs.videoPlayerCmd() %file
        self.app.dbg.p(2,"%s" %(cmd))
        os.system("(%s &)>/dev/null 2>&1" %(cmd))
