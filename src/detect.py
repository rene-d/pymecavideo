# -*- coding: utf-8 -*-
"""
    detect, a module for pymecavideo:
      this module implements the automatic detection of moving objects.
      
    Copyright (C) 2010 Jean-Baptiste Butet <ashashiwa@gmail.com>
    Copyright (C) 2010 Georges Khaznadar <georgesk@ofset.org>

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

import cv2.cv as cv
import cv2

from globdef import *


def filter_picture(parts, num, image, dossTemp):
    part = parts[num]
    
    if "QImage" in str(type(part)):
        part = QImage2CVImage(part, dossTemp)
        
    if type(image) == type("") and type(part) == type(""):
        image = cv2.imread(image, 1)
        part = cv2.imread(part, 1)
        point1, point2 = detect_part(part, image)
        return point2
    
    elif "iplimage" in str(type(part)) and "iplimage" in str(type(image)):
        points = detect_part(part, image)
        return points
    
    elif "QImage" in str(type(image)):
        image = QImage2CVImage(image, dossTemp)
        point1, point2 = detect_part(part, image)

        return (point2[0]+part.shape[1]/2, point2[1]+part.shape[0]/2)

    else:
        return "Type Error"



def detect_part(part, image):
    result = cv2.matchTemplate(image, part, cv.CV_TM_SQDIFF) #  CV_TM_CCOEFF
    m, M, point2, point1 = cv2.minMaxLoc(result)
    return point1, point2



def QImage2CVImage(img, dossierTemp):
    """ Converti une QImage en une image CV
    """
    fichImg = os.path.join(dossierTemp + "image.png")
    img.save(fichImg)
    img = cv2.imread(fichImg, 1)
    os.remove(fichImg)
    return img
    
    
