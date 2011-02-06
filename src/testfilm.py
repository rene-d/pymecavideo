#!/usr/bin/python
# -*- coding: utf-8 -*-

import cv
import sys, threading

class film:
    """
    Une classe pour accéder aux images d'un film
    """
    def __init__(self,filename):
        """
        le constructeur
        @param filename le nom d'un fichier video
        """
        self.filename=filename
        self.capture=cv.CreateFileCapture(self.filename)
        t=threading.Thread(target=self.autoTest)
        t.start()
        t.join(5.0) # attente de 5 secondes au plus
        

    def autoTest(self):
        self.ok=False
        try:
            self.frame=cv.QueryFrame(self.capture)
            self.num=0
            self.fps=cv.GetCaptureProperty(self.capture,cv.CV_CAP_PROP_FPS)
            self.framecount=cv.GetCaptureProperty(self.capture,cv.CV_CAP_PROP_FRAME_COUNT)
            self.ok=True
        except:
            pass

    def __int__(self):
        return int(self.ok)
    def __nonzero__(self):
        return self.ok
        

if __name__ == '__main__':
    if len(sys.argv)>1:
        vidfile=sys.argv[1]
        if film(vidfile):
            sys.exit(0)
        else:
            sys.exit(1)

