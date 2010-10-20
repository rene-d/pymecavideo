# -*- coding: utf-8 -*-

licence={}
licence['en']="""
    pymecavideo version %s:

    a program to track moving points in a video frameset
    
    Copyright (C) 2007-2008 Jean-Baptiste Butet <ashashiwa@gmail.com>
    
    Copyright (C) 2007-2008 Georges Khaznadar <georgesk@ofset.org>

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

licence['fr']=u"""
    pymecavideo version %s :

    un programme pour tracer les trajectoires des points dans une vidéo.
    
    Copyright (C) 2007-2008 Jean-Baptiste Butet <ashashiwa@gmail.com>
    
    Copyright (C) 2007-2008 Georges Khaznadar <georgesk@ofset.org>
    
    Ce projet est un logiciel libre : vous pouvez le redistribuer, le modifier selon les terme de la GPL (GNU Public License) dans les termes de la Free Software Foundation concernant la version 2 ou plus de la dite licence.
    
    Ce programme est fait avec l'espoir qu'il sera utile mais SANS AUCUNE GARANTIE. Lisez la licence pour plus de détails.
    
    <http://www.gnu.org/licenses/>.
"""


import sys, os

#
# Version 
#
VERSION = "5.2"

#
# Format des images extraites
#
EXT_IMG = '.jpg'


if sys.platform == 'win32':
    #
    # Les deuxlignes suivantes permettent de lancer le script pymecavideo.py depuis n'importe
    # quel répertoire  sans que l'utilisation de chemins
    # relatifs ne soit perturbée
    #
    PATH = os.path.dirname(os.path.abspath(sys.argv[0]))
    PATH = os.path.split(PATH)[0]
    os.chdir(PATH)
    sys.path.append(PATH)
    
    #On récupￃﾨre lￃﾠ le dossier "Application data" 
    #oￃﾹ devra ￃﾪtre enregistré les fichier "images_extraites"
    
    # On lit la clef de registre indiquant le type d'installation
    import win32api, win32con
    try:
        regkey = win32api.RegOpenKeyEx( win32con.HKEY_LOCAL_MACHINE, 'SOFTWARE\\pymecavideo', 0, win32con.KEY_READ )
        (value,keytype) = win32api.RegQueryValueEx(regkey, 'DataFolder' ) 
        APP_DATA_PATH = value
        if not os.path.exists(APP_DATA_PATH):
            os.mkdir(APP_DATA_PATH)
    except:
        APP_DATA_PATH = PATH
        
        
    sys.path.append(os.path.join(PATH, 'bin'))
    
    print "Dossier pymecavideo.exe", PATH
    print "Dossier data", APP_DATA_PATH

else:
    PATH = APP_DATA_PATH = ""
    
#
# Nom du dossier des images extraites
#
IMG_PATH = os.path.join(APP_DATA_PATH, "images_extraites")

#
# Nom du fichier de sortie AVI
#
AVI_OUT = os.path.join(IMG_PATH, "out.avi")

#
#
#
ERROR_FILE = os.path.join(APP_DATA_PATH, 'pyMecaVideo.exe' + '.log')


#
# Nom des fichiers "crop" et "video"
#
CROP = "crop"
VIDEO = "video"


#
# Gestion des Popen()
#
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