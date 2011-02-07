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


import sys, os
from PyQt4.QtGui import QDesktopServices
#from PyQt4.QtGui import *

#
# Version de pymecavideo
#
VERSION = "5.3"


def testerDossier(listDir, defaut = ""):
    for dir in listDir:
        if os.path.exists(dir):
            return dir
    return defaut
    
#
# Dossier de l'application
#

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

else:
    pass

#
# Dossier des données "temporaires" (video*.jpg, crop*.jpg, out.avi)
#
if sys.platform == 'win32':
    #On récupèreﾠ le dossier "Application data" 
    #On lit la clef de registre indiquant le type d'installation
    import win32api, win32con
    try:
        regkey = win32api.RegOpenKeyEx( win32con.HKEY_LOCAL_MACHINE, 'SOFTWARE\\pymecavideo', 0, win32con.KEY_READ )
        (value,keytype) = win32api.RegQueryValueEx(regkey, 'DataFolder' ) 
        APP_DATA_PATH = value
        if not os.path.exists(APP_DATA_PATH):
            os.makedirs(APP_DATA_PATH)
    except:
        APP_DATA_PATH = PATH
    sys.path.append(os.path.join(PATH, 'bin'))

else:
    datalocation=os.path.join("%s"%QDesktopServices.storageLocation(QDesktopServices.DataLocation),"pymecavideo")
    PATH = APP_DATA_PATH = datalocation


#
# Nom du dossier des images extraites et des vidéos créées
#
IMG_PATH = os.path.join(APP_DATA_PATH, "images_extraites")
NEWVID_PATH = os.path.join(APP_DATA_PATH, "videos_recodees")
if not os.path.exists(NEWVID_PATH):
    print "ok", NEWVID_PATH
    os.makedirs(NEWVID_PATH)
    print os.path.exists(NEWVID_PATH)

#
# Dossier gnuplot
#
def GetGnuplotPath():
    paths = os.environ['PATH'].split(os.pathsep)
    if 'PROGRAMFILES' in os.environ.keys():
        paths.append(os.environ['PROGRAMFILES'])
    GNUPLOT_PATH = None
    for p in paths:
        if os.access(os.path.join(p,"gnuplot"), os.X_OK):
            GNUPLOT_PATH = p
    if GNUPLOT_PATH != None:
        return os.path.join(GNUPLOT_PATH, "gnuplot", "binary")
    else:
        return ""
GNUPLOT_PATH = GetGnuplotPath()

# Dossier "home"
#
HOME_PATH = unicode(QDesktopServices.storageLocation(8), 'iso-8859-1')

#
# Dossier "video"
#
if sys.platform == 'win32':
    VIDEO_PATH = os.path.join(PATH,"data","video")
else:
    VIDEO_PATH = testerDossier((os.path.join("..","data","video"),
                                '/usr/share/pymecavideo/video',
                                '/usr/share/python-mecavideo/video'),
                                APP_DATA_PATH)

#
# Dossier pour testfilm.py
#

PYMECA_SHARE =testerDossier(('/usr/share/pymecavideo',
                             '/usr/share/python-mecavideo',
                             '.'),
                            '/usr/share/pymecavideo')
                             

#
# Dossier de pymecavideo.conf
#
if sys.platform == 'win32':
    CONF_PATH = APP_DATA_PATH
else:
    CONF_PATH = PATH

#
# Dossier des icones
#
if sys.platform == 'win32':
    ICON_PATH = os.path.join(PATH,"data","icones")
else:
    ICON_PATH = testerDossier((os.path.join("..","data","icones"),
    '/usr/share/python-mecavideo/icones','/usr/share/pymecavideo/icones'))
#
# Dossier des langues
#
if sys.platform == 'win32':
    LANG_PATH = os.path.join(PATH,"..","data","lang")
else:
    LANG_PATH = testerDossier((os.path.join("..","data","lang"),
    '/usr/share/pyshared/pymecavideo/lang','/usr/share/python-mecavideo/lang','/usr/share/pymecavideo/lang'))

#
# Dossier "data"
#
if sys.platform == 'win32':
    DATA_PATH = os.path.join(PATH,"data")
else:
    #DATA_PATH = os.path.join(PATH,"..","data")
    DATA_PATH = testerDossier((os.path.join("..","data"),
    '/usr/share/python-mecavideo/','/usr/share/pymecavideo/'))

#
# Dossier de l'aide
#
if sys.platform == 'win32':
    HELP_PATH = os.path.join(PATH,"data", "help")
else:
    HELP_PATH = testerDossier((os.path.join("..","data","help"),"/usr/share/doc/python-mecavideo/html",
                               "/usr/share/doc/HTML/fr/pymecavideo"))
#
# Nom du fichier de sortie AVI
#
AVI_OUT = os.path.join(IMG_PATH, "out.avi")


ERROR_FILE = os.path.join(APP_DATA_PATH, 'pymecavideo.exe' + '.log')

#
# Nom des fichiers "crop" et "video"
#
CROP = "crop"
VIDEO = "video"
SUFF = "%04d.jpg"

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

