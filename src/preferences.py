# -*- coding: utf-8 -*-

licence = """
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

# from interfaces.Ui_preferences import Ui_Dialog
from PyQt6.QtCore import QObject, QTimer
from PyQt6.QtWidgets import QMessageBox

import os, re, configparser, io

from version import Version
from vecteur import vecteur

class MonConfigParser(configparser.ConfigParser):
    """
    Analiseur de fichier de configuration qui sait triter les vecteurs
    """
    def __init__(self):
        configparser.ConfigParser. __init__(self)
        return

    def getvecteur(self, section, option):
        """
        @param section la section où on cherche
        @param option l'option que l'on cherche
        @return la valeur sous forme de vecteur en cas de réussite
          sinon par défaut, vecteur(0,0)
        """
        floatre = r"[+-]?(\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?"
        m = re.match(f"\\(({floatre}),[ ]?({floatre})\\)", self[section][option])
        if m:
            return vecteur(float(m.group(1)), float(m.group(5)))
        else:
            return vecteur(0,0)
    
class Preferences (QObject):
    def __init__(self, parent):
        QObject.__init__(self)
        
        self.app = parent
        self.app.dbg.p(3, "In : Preferences, preferences.py")

        self.conffile = os.path.join(self.app._dir("conf"), "pymecavideo.conf")
        self.config = MonConfigParser()

        # ajuste les valeurs par défaut
        d = self.defaults = self.config['DEFAULT']

        d['version']   = f"pymecavideo {Version}"
        d['proximite'] = "False"     # vecteurs tracés près du curseur
        d['lastVideo'] = ""          # vidéo consultée précédement
        d['videoDir']  = os.getcwd() # répertoire pour les vidéos
        d['niveauDbg'] = "0"         # niveau des messages de débogage
        d['sens_X']    = "1"         # sens dee abscisses
        d['sens_Y']    = "1"         # sens dee ordonnées
        d['taille_image'] = "(320,240)" # dimension de l'image de vidéo
        d['rotation']  = "0"         # rotation de l'image
        d['origine'] = "(320,240)"   # origine pour les pointages
        d['index_depart'] = "1"      # première image pointée
        d['etalon_m'] = "1.00"       # longueur de l'étalon en mètre
        d['etalon_px'] = "100"       # longueur de l'étalon en pixel
        d['etalon_org'] = "None"     # point 1 de l'étalon sur l'image
        d['etalon_ext'] = "None"     # point 2 de l'étalon sur l'image
        d['deltaT'] = "0.040"        # intervalle de temps entre deux images
        d['nb_obj'] = "1"            # nombre d'objets suivis
        # récupère les valeurs enregistrées
        self.load()
        return

    def __str__(self):
        """
        donne une représentation lisible de la configuration
        """
        with io.StringIO() as outfile:
            d = self.config["DEFAULT"]
            self.config.write(outfile)
            result = outfile.getvalue()
        return result

    def save(self):
        """
        Sauvegarde des préférences dans le fichier de configuration.
        """
        with open(self.conffile, "w") as outfile:
            d = self.config["DEFAULT"]
            d["version"] = f"pymecavideo {Version}"
            d["lastvideo"] = str(self.app.pointage.filename)
            self.config.write(outfile)
        return

    def load(self):
        if os.path.exists(self.conffile):
            try:
                self.config.read(self.conffile)
            except :
                QTimer.singleShot(
                    50,
                    lambda: QMessageBox.information(
                        self.app,
                        self.tr("Erreur de lecture de la configuration"),
                        self.tr("Peut-être un ancien format de fichier de configuration ? On recommence avec une configuration neuve.")))
        return
