# -*- coding: utf-8 -*-

licence="""
    preferences is a a file of the project pymecavideo:
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
        # ajuste les valeurs par défaut
        self.proximite=False
        self.lastVideo=""
        self.videoDir=os.getcwd()
        self.niveauDbg=0 # niveau d'importance des messages de débogage
        # récupère les valeurs enregistrées
        self.load()

    def __str__(self):
        """
        Renvoie une chaîne représentant les préférences, lisible par un humain
        """
        result=self.app.tr("Proximite de la souris %1").arg(self.proximite)
        result +=self.app.tr("; derniere video %1").arg(self.lastVideo)
        result +=self.app.tr("; videoDir %1").arg(self.videoDir)
        result +=self.app.tr("; niveau courant de debogage %1").arg(self.niveauDbg)
        return "%s" %result

    def save(self):
        """
        Sauvegarde des préférences dans le fichier de configuration.
        """
        f=open(self.conffile,"w")
        self.app.dbg.p(9,"sauvegarde des preferences dans  %s" %self.conffile)
        self.app.dbg.p(9, "%s" %self)
        pickle.dump((self.proximite,self.lastVideo,self.videoDir,self.niveauDbg),f)
        f.close()
        
    def load(self):
        if os.path.exists(self.conffile):
            try:
                f=open(self.conffile,"r")
                (self.proximite,self.lastVideo,self.videoDir,self.niveauDbg) = pickle.load(f)
                f.close()
                self.app.dbg=Dbg(self.niveauDbg)
            except:
                self.app.dbg.p(2,"erreur en lisant %s" %self.conffile)
                pass
        
    def setFromDialog(self):
        """
        Règle les préférences à l'aide d'un dialogue
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
        p.addItem(self.app.tr("Visibles partout"))
        p.addItem(self.app.tr("Visible pres de la souris"))
        if self.proximite:
            p.setCurrentIndex(1)
        else:
            p.setCurrentIndex(0)
        retval=d.exec_()
        if retval:
            ######################################################
            # prend les valeurs depuis le dialogue
            ######################################################
            self.niveauDbg=ui.spinBoxDbg.value()
            self.app.dbg=Dbg(self.niveauDbg)
            
            self.proximite=(ui.comboBoxProximite.currentIndex() == 1)
            self.app.visibilite_vitesses()
            
            self.save()
        return
        
