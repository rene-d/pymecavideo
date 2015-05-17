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

# from Ui_preferences import Ui_Dialog
import pickle
import os
import os.path


class Preferences:
    def __init__(self, parent):

        self.app = parent
        self.app.dbg.p(3, "In : Preferences, preferences.py")

        self.conffile = os.path.join(self.app._dir("conf"), "pymecavideo.conf")
        # ajuste les valeurs par défaut
        self.proximite = False
        self.lastVideo = ""
        self.videoDir = os.getcwd()
        self.niveauDbg = 0  # niveau d'importance des messages de débogage
        # récupère les valeurs enregistrées
        self.load()

    def __str__(self):
        """
        Renvoie une chaîne représentant les préférences, lisible par un humain
        """
        result = self.app.tr("Proximite de la souris {0}").format(self.proximite)
        result += self.app.tr("; derniere video {0}").format(self.lastVideo)
        result += self.app.tr("; videoDir {0}").format(self.videoDir)
        return "%s" % result

    def save(self):
        """
        Sauvegarde des préférences dans le fichier de configuration.
        """
        f = open(self.conffile, "w")
        self.app.dbg.p(6, "sauvegarde des preferences dans  %s" % self.conffile)
        self.app.dbg.p(6, "%s" % self)
        try:
            self.lastVideo = unicode(self.lastVideo, 'utf8')
        except TypeError:
            pass
        pickle.dump((self.proximite, self.lastVideo, self.videoDir), f)
        f.close()

    def load(self):
        if os.path.exists(self.conffile):
            try:
                f = open(self.conffile, "r")
                (self.proximite, self.lastVideo, self.videoDir) = pickle.load(f)
                f.close()
            except:
                self.app.dbg.p(2, "erreur en lisant %s" % self.conffile)
                self.app.dbg.p(2, "effacement du répertoire temporaire de pymecavideo")
                pass
        
        
