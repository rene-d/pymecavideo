# -*- coding: utf-8 -*-

licence="""
    preferences is a a file of the project pymecavideo:
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

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from Ui_preferences import Ui_Dialog
from dbg import Dbg
import vecteur, commands
import pickle, os, os.path

class Preferences:
    def __init__(self, parent):
        self.app=parent
        self.conffile=os.path.join(self.app._dir("conf"),"pymecavideo.conf")
        # ajuste les valeurs par dÃ©faut
        self.proximite=False
        self.lastVideo=""
        self.videoDir=os.getcwd()
        self.detect_video_players()
        self.niveauDbg=0 # niveau d'importance des messages de dÃ©bogage
        # rÃ©cupÃ¨re les valeurs enregistrÃ©es
        self.load()

    def __str__(self):
        """
        Renvoie une chaÃ®ne reprÃ©sentant les prÃ©fÃ©rences, lisible par un humain
        """
        result="Proximite de la souris %s" %self.proximite
        result +="; derniere video %s" %self.lastVideo
        result +="; videoDir %s" %self.videoDir
        result +="; niveau courant de debogage %s" %self.niveauDbg
        result +="; dictionnaire des lecteurs video %s" %self.videoPlayers
        return result

    def detect_video_players(self):
        """dÃ©tecte les players dispnibles sur le systÃ¨me"""
        
        self.videoPlayers = {}
        players = {"xine":"xine -l %s",
                           "vlc" :"vlc -L %s", "mplayer" :"mplayer -loop 0 %s"}
        
        if self.app.platform.lower()=="linux":
            for player in players :
                # si linux/unix
                status, output = commands.getstatusoutput("whereis "+player+"|grep bin")
                if status== 0 :
                    self.videoPlayers[player]=players[player]
        # si windows on regarde Vlc
        elif self.app.platform.lower()=="windows":
            pf_path = os.environ["PROGRAMFILES"]
            vlc_path = os.path.join(pf_path, "VideoLAN", "VLC", "vlc.exe")
            if os.path.exists(vlc_path) :
                self.videoPlayers["vlc"] = vlc_path# + " -L "

        if "xine" in self.videoPlayers.keys() :
            self.videopref="xine"
        elif "vlc" in self.videoPlayers.keys() :
            self.videopref="vlc"
        elif "mplayer" in self.videoPlayers.keys() :
            self.videopref="mplayer"
        else :
            warning =QMessageBox.warning(None,u"ATTENTION : pas de lecteurs vidÃ©os trouvÃ©s","Vous devez installer VLC, fflpay, -ou MPLAYER ou XINE si vous Ãªtes sous linux-",QMessageBox.Ok,QMessageBox.Ok)
            import sys
            sys.exit(-1)#fais une erreur...mais fais ce qu'on veut ;)
        self.app.player = self.videoPlayers[self.videopref]
        
        
        
        
        
    def save(self):
        """
        Sauvegarde des prÃ©fÃ©rences dans le fichier de configuration.
        """
        f=open(self.conffile,"w")
        self.app.dbg.p(9,"sauvegarde des preferences dans  %s" %self.conffile)
        self.app.dbg.p(9, "%s" %self)
        pickle.dump((self.proximite,self.lastVideo,self.videoDir,self.videopref,self.niveauDbg),f)
        f.close()
        
    def load(self):
        if os.path.exists(self.conffile):
            try:
                f=open(self.conffile,"r")
                (self.proximite,self.lastVideo,self.videoDir,self.videopref,self.niveauDbg) = pickle.load(f)
                f.close()
                self.app.dbg=Dbg(self.niveauDbg)
            except:
                self.app.dbg.p(2,"erreur en lisant %s" %self.conffile)
                pass
        
    def videoPlayerCmd(self):
        cmd=self.videoPlayers[self.videopref]
        return cmd

    def setFromDialog(self):
        """
        RÃ¨gle les prÃ©fÃ©rences Ã  l'aide d'un dialogue
        """
        self.app.dbg.p(2,"appel du dialogue des preferences")
        import Ui_preferences
        d=QDialog()
        ui=Ui_Dialog()
        ui.setupUi(d)
        #########################################################
        # envoie les valeurs courantes dans le dialogue
        #########################################################
        ui.spinBoxDbg.setValue(self.niveauDbg)
        p=ui.comboBoxProximite
        p.addItem(u"Visibles partout")
        p.addItem(u"Visible prÃ¨s de la souris")
        if self.proximite:
            p.setCurrentIndex(1)
        else:
            p.setCurrentIndex(0)
        p=ui.comboBoxVideoPLayer
        vp=self.videoPlayers.keys()
        for cmd in vp:
            p.addItem(cmd)
        p.setCurrentIndex(vp.index(self.videopref))
        retval=d.exec_()
        if retval:
            ######################################################
            # prend les valeurs depuis le dialogue
            ######################################################
            self.niveauDbg=ui.spinBoxDbg.value()
            self.app.dbg=Dbg(self.niveauDbg)
            
            self.proximite=(ui.comboBoxProximite.currentIndex() == 1)
            self.app.visibilite_vitesses()
            
            self.videopref=str(ui.comboBoxVideoPLayer.currentText())
            self.save()
        return
        
