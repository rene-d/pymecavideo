# -*- coding: utf-8 -*-
"""
    suivi_auto, a module for pymecavideo:
      a program to track moving points in a video frameset
      
    Copyright (C) 2007 Jean-Baptiste Butet <ashashiwa@gmail.com>
    Copyright (C) 2023 Georges Khaznadar <georgesk@debian.org>

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

from version import Version
from PyQt6.QtCore import QStandardPaths, QTimer
from PyQt6.QtGui import QPixmap, QCursor
from PyQt6.QtWidgets import QApplication

import subprocess
import os
import sys
licence = {}
licence['en'] = """
    pymecavideo version %s:

    a program to track moving points in a video frameset
    
    Copyright (C) 2007-2008 Jean-Baptiste Butet <ashashiwa@gmail.com>
    
    Copyright (C) 2007-2018 Georges Khaznadar <georgesk.debian.org>

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

licence['fr'] = u"""
    pymecavideo version %s :

    un programme pour tracer les trajectoires des points dans une vidéo.
    
    Copyright (C) 2007-2008 Jean-Baptiste Butet <ashashiwa@gmail.com>
    
    Copyright (C) 2007-2018 Georges Khaznadar <georgesk.debian.org>
    
    Ce projet est un logiciel libre : vous pouvez le redistribuer, le modifier selon les terme de la GPL (GNU Public License) dans les termes de la Free Software Foundation concernant la version 3 ou plus de la dite licence.
    
    Ce programme est fait avec l'espoir qu'il sera utile mais SANS AUCUNE GARANTIE. Lisez la licence pour plus de détails.
    
    <http://www.gnu.org/licenses/>.
"""


#
# Version de pymecavideo
#
VERSION = Version


def testerDossier(listDir, defaut=""):
    for dir_ in listDir:
        if os.path.exists(dir_):
            return dir_
    return defaut


FILE_ENCODING = sys.getfilesystemencoding()
DEFAUT_ENCODING = "utf-8"

######################################################################################


def toFileEncoding(path):
    try:
        path = path.decode(DEFAUT_ENCODING)
        return path.encode(FILE_ENCODING)
    except:
        return path
#######################################################################################
# HOME_PATH : Dossier des documents
# APP_PATH : Dossier du lancement de l'application pymecavideo
#CONF_PATH : QStandardPaths.locate(QStandardPaths.StandardLocation.AppDataLocation, "pymecavideo/")
# DATA_PATH : Dossier contenant les datas, selon scenario
#ICON_PATH : DATA_PATH / icones
#LANG_PATH : DATA_PATH / lang
#HELP_PATH : DATA_PATH / lang
#VIDEO_PATH : DATA_PATH / videos


# APP_PATH

    #
    # Les deuxlignes suivantes permettent de lancer le script pymecavideo.py depuis n'importe
    # quel répertoire  sans que l'utilisation de chemins
    # relatifs ne soit perturbée
    #
PATH = os.path.dirname(os.path.abspath(sys.argv[0]))
sys.path.append(PATH)
APP_PATH = PATH

# DATA_PATH
if sys.platform == 'win32':
    DATA_PATH = os.path.join(APP_PATH, "data")
else:
    DATA_PATH = testerDossier((os.path.join("..", "data"),
                               '/usr/share/python3-mecavideo/', '/usr/share/pymecavideo/'))

# CONF_PATH
CONF_PATH = QStandardPaths.locate(QStandardPaths.StandardLocation.AppDataLocation, "pymecavideo/")

# HOME_PATH
HOME_PATH = QStandardPaths.locate(QStandardPaths.StandardLocation.HomeLocation, "")

# DOCUMENTS_PATH
DOCUMENT_PATH = QStandardPaths.locate(QStandardPaths.StandardLocation.DocumentsLocation, "")

# DOSSIERS
#
# dossier des icones
#
ICON_PATH = testerDossier(
    (os.path.join(DATA_PATH, "icones"), os.path.join("..", "data", "icones"),
     '/usr/share/python3-mecavideo/icones',
     '/usr/share/pymecavideo/icones',
     '/usr/share/icons')
)

#
# Dossier des langues
#
LANG_PATH = testerDossier((os.path.join(DATA_PATH, "lang"), os.path.join("..", "data", "lang"),
                           '/usr/share/pyshared/pymecavideo/lang', '/usr/share/python3-mecavideo/lang',
                           '/usr/share/pymecavideo/lang'))
#
# Dossier des vidéos
#
VIDEO_PATH = testerDossier((os.path.join(DATA_PATH, "video"), os.path.join("..", "data", "video"),
                            '/usr/share/pyshared/pymecavideo/video', '/usr/share/python3-mecavideo/video',
                            '/usr/share/pymecavideo/video'))

#
# Dossier de l'aide
#
HELP_PATH = testerDossier((os.path.join(DATA_PATH, "help"), os.path.join("..", "data", "help"), "/usr/share/doc/python-mecavideo/html",
                           "/usr/share/doc/HTML/fr/pymecavideo"))


ERROR_FILE = os.path.join(CONF_PATH, 'pymecavideo.exe' + '.log')


def GetChildStdErr():
    """ Renvoie le handler par défaut pour les Popen()
        (pour contourner un bug ... sous windows)
    """
    if sys.platform == 'win32':
        import win32process

        if hasattr(sys.stderr, 'fileno'):
            childstderr = sys.stderr
        elif hasattr(sys.stderr, '_file') and hasattr(sys.stderr._file, 'fileno'):
            childstderr = sys.stderr._file
        else:
            # Give up and point child stderr at nul
            childStderrPath = 'nul'
            childstderr = open(childStderrPath, 'a')
        return childstderr, win32process.CREATE_NO_WINDOW
    else:
        return None, 0

def _translate(context, text, disambig):
    return QApplication.translate(context, text, disambig)


def beauGrosCurseur(widget):
    """
    Définit un beau gros curseur rouge immanquable pour un widget
    @param widget le widget affecté par le curseur
    """
    cible_icon = os.path.join(ICON_PATH, "curseur_cible.svg")
    pix = QPixmap(cible_icon).scaledToHeight(32)
    cursor = QCursor(pix)
    widget.setCursor(cursor)
    widget.setMouseTracking(True)
    return
    
inhibitions = []; # liste de mots-clés pour inhiber des actions trop rapides

def inhibe(motcle, duree):
    """
    Qt 5.15 a un bug : certains évenements sont lancés deux fois
    On peut y remédier avec un timer.

    Cette fonction teste si un mot-clé est dans la liste globdef.inhibe
    s'il n'y est pas, elle l'y place et fait en sorte de l'effacer
    après une durée de duree millisecondes

    @param motcle le mot-clé d'inhibition
    @param duree la durée du tabou sur le mot-clé

    @return vrai si le mot-clé est encore là dans la liste des inhibitions,
      faux s'il n'était pas là (et alors il y est placé pour quelques temps)
    """
    result = motcle in inhibitions
    if not result:
        inhibitions.append(motcle)
        def efface(mot):
            def callback():
                if mot in inhibitions:
                    inhibitions.remove(mot)
                return
            return callback
        QTimer.singleShot(duree, efface(motcle))
    return result
