# -*- coding: utf-8 -*-
import cv
from cv import *

def filter_picture(part,image):
    if type(image)==type("") and type(part)==type("") :
        image=cv.LoadImage(image,1)
        part=cv.LoadImage(part,1)
        point1, point2 = detect_part(part,image)
        #print "P1,P2", point1, point2
        return point2
    elif "iplimage" in str(type(part)) and "iplimage" in str(type(image)):
        points = detect_part(part,image)
        #print "point", points
        return points
    elif "QImage" in str(type(part)) and "QImage" in str(type(image)):
        part.save("part.png")
        image.save("image.png")
        image=cv.LoadImage("image.png",1)
        part=cv.LoadImage("part.png",1)
        point1, point2 = detect_part(part,image)
        #print "P1,P2__", point1, point2
        return point2
        
    else :
        return "Type Error"

def detect_part(part,image):

    resultW = image.width - part.width + 1
    resultH = image.height - part.height +1
    print resultW, resultH
    result = cv.CreateImage((resultW, resultH), IPL_DEPTH_32F, 1)
    cv.MatchTemplate(image, part,result, cv.CV_TM_SQDIFF)
    m, M, point2, point1 = cv.MinMaxLoc(result)
    #print  point1, point2
    return point1, point2

#filter_picture("modele.png", "cible.png")
#image=cv.LoadImage("modele.png",1)
#icon=cv.LoadImage("cible.png",1)
#filter_picture(image, icon)