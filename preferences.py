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
        self.conffile=self.app._dir("ressources")+"/"+"pymecavideo.conf"
        # ajuste les valeurs par défaut
        self.echelle_v=1.0
        self.proximite=False
        self.lastVideo=""
        self.videoDir=os.getcwd()
        self.detect_video_players()
        self.niveauDbg=0 # niveau d'importance des messages de débogage
        # récupère les valeurs enregistrées
        self.load()
    def detect_video_players(self):
        """détecte les players dispnibles sur le système"""
        self.videoPlayers = {}
        players = {"xine":"xine -l %s",
                           "vlc" :"vlc -L %s", "mplayer" :"mplayer -loop 0 %s"}
        for player in players :
            status, output = commands.getstatusoutput("whereis "+player+"|grep bin")
            if status== 0 :
                self.videoPlayers[player]=players[player]


        if "xine" in self.videoPlayers.keys() :
            self.videopref="xine"
        elif "vlc" in self.videoPlayers.keys() :
            self.videopref="vlc"
        elif "mplayer" in self.videoPlayers.keys() :
            self.videopref="mplayer"
        else :
            warning =QMessageBox.warning(None,u"ATTENTION : pas de lecteurs vidéos trouvés","Vous devez installer VLC, MPLAYER ou XINE",QMessageBox.Ok,QMessageBox.Ok)
            import sys
            sys.exit(-1)#fais une erreur...mais fais ce qu'on veut ;)

    def save(self):
        f=open(self.conffile,"w")
        pickle.dump((self.echelle_v,self.proximite,self.lastVideo,self.videoDir,self.videopref,self.niveauDbg),f)
        f.close()
        
    def load(self):
        if os.path.exists(self.conffile):
            try:
                f=open(self.conffile,"r")
                (self.echelle_v,self.proximite,self.lastVideo,self.videoDir,self.videopref,self.niveauDbg) = pickle.load(f)
                f.close()
            except:
                self.app.dbg.p(2,"erreur en lisant %s" %self.conffile)
                pass
        
    def videoPlayerCmd(self):
        cmd=self.videoPlayers[self.videopref]
        return cmd

    def setFromDialog(self):
        import Ui_preferences
        d=QDialog()
        ui=Ui_Dialog()
        ui.setupUi(d)
        #########################################################
        # envoie les valeurs courantes dans le dialogue
        #########################################################
        ui.echelle_vEdit.setText(str(self.app.echelle_v))
        ui.spinBoxDbg.setValue(self.niveauDbg)
        p=ui.comboBoxProximite
        p.addItem(u"Visibles partout")
        p.addItem(u"Visible près de la souris")
        if self.proximite:
            p.setCurrentIndex(1)
        else:
            p.setCurrentIndex(0)
        p=ui.comboBoxVideoPLayer
        vp=self.videoPlayers.keys()
        for cmd in vp:
            p.addItem(cmd)
        #print self.videopref
        p.setCurrentIndex(vp.index(self.videopref))
        retval=d.exec_()
        if retval:
            ######################################################
            # prend les valeurs depuis le dialogue
            ######################################################
            self.app.echelle_v=float(ui.echelle_vEdit.text())
            self.app.setEchelle_v()

            self.niveauDbg=ui.spinBoxDbg.value()
            self.app.dbg=Dbg(self.niveauDbg)
            
            self.proximite=(ui.comboBoxProximite.currentIndex() == 1)
            self.app.visibilite_vitesses()
            
            self.videopref=str(ui.comboBoxVideoPLayer.currentText())
            self.save()
        return
        
