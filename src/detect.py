# -*- coding: utf-8 -*-
"""
    detect, a module for pymecavideo:
      this module implements the automatic detection of moving objects.
      
    Copyright (C) 2010 Jean-Baptiste Butet <ashashiwa@gmail.com>
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

import os.path
import tempfile, time

import cv2
import numpy as np

from globdef import *


import functools


def time_it(func):
    """Timestamp decorator for dedicated functions"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()                 
        result = func(*args, **kwargs)
        elapsed = time.time() - start
        mlsec = repr(elapsed).split('.')[1][:3]
        readable = time.strftime("%H:%M:%S.{}".format(mlsec), time.gmtime(elapsed))
        print('Function "{}": {} sec'.format(func.__name__, readable))
        return result
    return wrapper


#@time_it
def filter_picture(parts, num, image, points=None):
    """
    Trouve la position d'une image partielle dans une image donnée
    @param parts une liste d'images partielles
    @param num un index signalant l'image active (couramment seul l'index zéro
    est supporté)
    @param image l'image où on va chercher à trouver le motif partiel
    @param points liste de points près desquels il est plus vraisemblable
    de trouver le motif.
    @return les coordonnées d'un point, résultant du suivi automatique du
    motif partiel dans l'image.
    """
    part  = parts [num]
 
    if points:
        point = points[num]
    else:
        point=None

    if "QImage" in str(type(part)):
        part = QImage2CVImage(part)

    if type(image) == type("") and type(part) == type(""):
        image = cv2.imread(image, 1)
        part = cv2.imread(part, 1)
        point = detect_part(part, image, point)
        return (point[0]+part.shape[1]/2, point[1]+part.shape[0]/2)
    
    elif "iplimage" in str(type(part)) and "iplimage" in str(type(image)):
        point = detect_part(part, image, point)
        return (point[0]+part.shape[1]/2, point[1]+part.shape[0]/2)
    
    elif "QImage" in str(type(image)):
        image = QImage2CVImage(image) 
        point = detect_part(part, image, point) #TODO 130ms
        return (point[0]+part.shape[1]/2, point[1]+part.shape[0]/2)

    else:
        return "Type Error"
#@time_it
def gaussMatrix(forme, sommet, hauteur, largeur, inverse=False):
    """
    renvoie une matrice de valeurs qui forment un pic gaussien autour
    d'un sommet de coordonnées données, variant entre 0 et hauteur. Si
    inverse est vrai, le sommet est à zéro, et la valeur s'approche de 
    "hauteur" quand on s'éloigne du sommet.
    @param forme les paramètres de forme de la matrice (lignes, colonnes)
    @param sommet coordonnées du sommet
    @param hauteur la hauteur au sommet
    @param largeur la distance par rapport au sommet, à mi-hauteur
    @param inverse doit être vrai si on veur inverser la gaussienne
    """
    x=np.arange(0,forme[1], 1)
    y=np.arange(0,forme[0], 1)
    y=y[:,np.newaxis]
    result=np.exp(-4 * np.log(2) * ((x-sommet[0])**2 + (y-sommet[1])**2) / largeur**2)
    if inverse:
        maxv=hauteur*np.ones_like(result)
        result=maxv-result
    return result

#@time_it
def detect_part(part, image, point=None):
    """
    Détecte une image partielle dans une image complète
    @param part l'image partielle, le motif à trouver
    @param image l'image totale où l'on cherche le motif.
    @param point s'il est défini, un point près duquel il est plus probable
    de trouver ce qu'on cherche
    @return l'emplacement où se trouve le motif recherché
    """
    import numpy as np
    ##méthode 1 : 
    result = cv2.matchTemplate(image, part, cv2.TM_SQDIFF) #  cv2.TM_CCOEFF  Pour AMELIORER la vitesse, une possiblité est de réduire "image"
    
    ##########################################################
    #À ce point, result est une carte des coïncidences possibles
    #entre le motif "part" et l'image complète "image"
    #iI faudrait donner un peu plus de vraisemblance aux coïncidences
    #proches du dernier point détecté.
    ##########################################################    
    if point:
        flou=2
        vraisemblable=gaussMatrix(result.shape,point,np.amax(result),flou*(part.shape[0]+part.shape[1]), inverse=True)
        result = result+vraisemblable

    ########## ceci minimise les chances de trouver loin ###########
    m, M, minloc, maxloc = cv2.minMaxLoc(result)
    return minloc
    
 
#@time_it
#def QImage2CVImage_(img, dossierTemp):
    #""" Convertit une QImage en une image CV
    #"""
    #fichImg = os.path.join(dossierTemp + "image.png")
    #img.save(fichImg) #100ms
    #img_cv = cv2.imread(fichImg, 1)
    #os.remove(fichImg)
    #return img_cv
    

def QImage2CVImage(incomingImage):
    '''  Converts a QImage into an opencv MAT format  '''

    incomingImage = incomingImage.convertToFormat(4)

    width = incomingImage.width()
    height = incomingImage.height()

    ptr = incomingImage.bits()
    ptr.setsize(incomingImage.byteCount())
    arr = np.array(ptr).reshape(height, width, 4)  #  Copies the data
    return arr



