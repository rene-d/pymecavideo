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

import cv
from cv import *
from globdef import *
import os.path, tempfile

def filter_picture(part,image):
    imgPref=tempfile.NamedTemporaryFile(delete=False).name
    partImg=os.path.join(imgPref+"part.png")
    
    img=os.path.join(imgPref+"image.png")
    print imgPref, partImg
    if type(image)==type("") and type(part)==type("") :
        image=cv.LoadImage(image,1)
        part=cv.LoadImage(part,1)
        point1, point2 = detect_part(part,image)
        return point2
    elif "iplimage" in str(type(part)) and "iplimage" in str(type(image)):
        points = detect_part(part,image)
        return points
    elif "QImage" in str(type(part)) and "QImage" in str(type(image)):
        part.save(partImg)
        image.save(img)
        image=cv.LoadImage(img,1)
        part=cv.LoadImage(partImg,1)
        point1, point2 = detect_part(part,image)
        print point2
        #os.remove(img)
        #os.remove(partImg)
        return point2
        
    else :
        return "Type Error"
    

def detect_part(part,image):

    resultW = image.width - part.width + 1
    resultH = image.height - part.height +1
    result = cv.CreateImage((resultW, resultH), IPL_DEPTH_32F, 1)
    cv.MatchTemplate(image, part,result, cv.CV_TM_SQDIFF)
    m, M, point2, point1 = cv.MinMaxLoc(result)
    return point1, point2
