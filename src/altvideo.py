# -*- coding: utf-8 -*-

licence={}
licence['en']="""
    altvideo.py is part of the package pymecavideo
    
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

from PyQt4.QtCore import *
from PyQt4.QtGui import *

import subprocess, os.path, re

def altVideo(filename, userdir, warning=True):
    """
    recode une vidéo dans un conteneur AVI à l'aide de ffmpeg
    @param filename le nom du fichier vidéo d'entrée
    @param userdir un réperoire où écrire la nouvelle vidéo
    @param warning vrai pour avoir un message d'avertissement.
    @return le chemin vers la vidéo nouvellement créée, sinon une chaîne vide
    """
    sansSuffixe=os.path.basename(filename)
    match=re.match("(.*)\.(.*)$",sansSuffixe)
    sansSuffixe=match.group(1)
    dest=os.path.join(userdir,sansSuffixe+".avi")
    if warning:
        QMessageBox.information(None,
                                QApplication.translate("Dialog", "Recodage de la vidéo", None, QApplication.UnicodeUTF8),
                                QApplication.translate("Dialog", "La vidéo choisie (%1) n'est pas facilement traitée par la bibliothèque OpenCV. Elle va être recodée dans un conteneur AVI (%2). La copie de la vidéo sera supprimée à la fermeture de cette application.", None, QApplication.UnicodeUTF8).arg(filename).arg(dest))
        
    cmd="mencoder %s -oac copy -ovc lavc -o %s >/dev/null 2>&1" %(filename,dest)
    if subprocess.call(cmd, shell=True)==0:
        return dest
    else:
        return ""

if __name__=="__main__":
    import sys
    print altVideo(sys.argv[1],"/tmp", warning=False)
    
