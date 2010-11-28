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

class videoImage:
    """
    Une classe pour la gestion des images que contient une vidéo
    """

    def __init__(self, videoFileName=None):
        """
        Le constructeur
        """
        self.videoFileName=videoFileName
        self.chemin_image=None
        self.image_max=None
        self.framerate = 25      # vitesse des vidéos pas défaut
        self.deltaT = 0.04       # durée 40 ms par défaut : 25 images/s
        self.ffmpeg = None       # on ignore le nom de la commande au début
        self.platform = None     # de même on ignore la plateforme.

        self.initPlatform()

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

    def extract_image(self, index, prefs, force=False, sortie=False):
        """
        extrait l'image d'index "index" de la video à l'aide de ffmpeg
        et l'enregistre sur le disque.
        @param index désigne l'image
        @param prefs une structure de préférences de pymecavideo
        @param force booléen pour forcer la réécriture d'une image même si elle existe déjà
        @param sortie booléen vrai si on a besoin de récupérer la sortie standard de la commande qui est lancée
        """

        imfilename=os.path.join(IMG_PATH, VIDEO + SUFF %index)
        output = ""

        if os.path.isfile(imfilename) and force==False: #si elle existe déjà et , ne fait rien
            self.chemin_image = imfilename
        else : #sinon, extrait depuis la video
            #attention au cas de la dernière image.
            i=1
            args=[self.ffmpeg,"""-i""", self.videoFileName,"""-ss""",str((index-i)*self.deltaT),
                  """-vframes""",str(1),"""-f""","""image2""","""-vcodec""","""mjpeg""",imfilename]
            childstderr, creationflags = GetChildStdErr()
            cmd0 = subprocess.Popen(args=args,
                                    stderr=subprocess.PIPE,
                                    stdin = childstderr,
                                    stdout = childstderr,
                                    creationflags = creationflags)
            cmd0.wait()
            cmd0.poll()
            if sortie :
                sortie_ = cmd0.communicate()
           
            returncode =  cmd0.returncode
            if returncode==0:
                self.chemin_image = imfilename
            elif returncode==1 and prefs.lastVideo != "":
                print "erreur", returncode
                self.chemin_image = ""
                mauvaisevideo = QMessageBox.warning(self,QApplication.tr(unicode("ERREUR","utf8")), QString(QApplication.tr(unicode("La video que vous tentez d'ouvrir n'est pas dans un format lisible.\n Merci d'en ouvrir une autre ou de l'encoder autrement","utf8"))), QMessageBox.Ok,QMessageBox.Ok)
                prefs.lastVideo = ""
                prefs.save()
                # self.close()
            else:
                print "erreur", returncode
              
            #elif returncode > 256 :

            if sortie:
                return sortie_
          
    def recupere_avi_infos(self):
        """Ouvre une vidéo AVI et retourne son framerate ainsi que le nombre d'images de la vidéo.
        met à jour self.framerate, self.deltaT, self.image_max
        """
        self.framerate = 25
        duration=0
        videospec=self.extract_image(1,self.prefs, force=True, sortie=True)[1]
        try:
            patternRate=re.compile(".*Video.* ([.0-9]+) tbr.*")
            patternDuration=re.compile(".*Duration.* (\\d+):(\\d+):([.0-9]*),.*")
            l=videospec.split("\n")
            for line in l:
                m=patternRate.match(line)
                if m:
                    self.framerate=float(m.group(1))
                m=patternDuration.match(line)
                if m:
                    h=int(m.group(1))
                    min=int(m.group(2))
                    s=float(m.group(3))
                    duration=3600*h+60*min+s
        except:
            self.dbg.p(0, QApplication.tr("Impossible de lire %s" %self.videoFileName))
        self.image_max=int(duration*self.framerate)
        self.deltaT=1.0/self.framerate

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
