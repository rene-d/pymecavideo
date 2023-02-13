# -*- coding: utf-8 -*-
"""
    detect, a module for pymecavideo:
      this module implements the automatic detection of moving objects.
      
    Copyright (C) 2010 Jean-Baptiste Butet <ashashiwa@gmail.com>
    Copyright (C) 2007-2023 Georges Khaznadar <georgesk.debian.org>

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
import tempfile
import time

import cv2
import numpy as np

from globdef import *
from vecteur import vecteur


# @time_it
def filter_picture(part, image, zone_proche=None):
    """
    Trouve la position d'une image partielle dans une image donnée
    @param part une images partielle (au format d'openCV)
    @param image une image où chercher (même format)
    @param zone_proche un vecteur près duquel pourrait bien se trouver
      l'image recherchée ; peut être None, auquel cas on recherche dans
      toute l'image (ACTUELLEMENT ON N'EN TIENT PAS COMPTE)
    @return les coordonnées d'un point, résultant du suivi automatique
      du motif partiel dans l'image.
    """
    point = detect_part(part, image, zone_proche)  # TODO 130ms
    return point

# @time_it



# @time_it
def detect_part(part, image, point=None):
    """
    Détecte une image partielle dans une image complète
    @param part l'image partielle, le motif à trouver
    @param image l'image totale où l'on cherche le motif.
    @param point s'il est défini, un point près duquel il est plus probable
      de trouver ce qu'on cherche ; ce point est en haut à gauche de l'image
      partielle
    @return l'emplacement où se trouve le motif recherché
    """
    if point:
        # on choisit un rayon assez petit par rapport à la taille de l'image
        # afin de faire la première recherche dans un extrait de l'image
        r = (image.shape[0]+image.shape[1]) // 10
        centre = (point[0] + part.shape[0] // 2, point[1] + part.shape[1] // 2)
        hg = (centre[0] - r, centre[1] - r) # haut gauche
        bd = (centre[0] + r, centre[1] + r) # bas droite
        extrait = image[hg[1]:bd[1], hg[0]:bd[0], :]
        # on vérifie que l'extrait soit assez grand
        if extrait.shape[0] > part.shape[0] and \
           extrait.shape[1] > part.shape[1]:
            matched = cv2.matchTemplate(extrait, part, cv2.TM_SQDIFF)
            m, M, minloc, maxloc = cv2.minMaxLoc(matched)
            # si le minimum `m` est assez bas, on considère qu'on a trouvé
            tolerance = 120 * part.shape[0] * part.shape[1]
            if m < tolerance:
                return (minloc[0]+hg[0], minloc[1]+hg[1])

    ####### si ça n'a pas marché on recherche dans toute l'image ########
    matched = cv2.matchTemplate(image, part, cv2.TM_SQDIFF)
    m, M, minloc, maxloc = cv2.minMaxLoc(matched)
    return minloc
