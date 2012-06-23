#!/usr/bin/python
# -*- coding: utf-8 -*-

import cv
import sys, threading, os.path

class film:
    """
    Une classe pour accéder aux images d'un film
    """
    def __init__(self,filename):
        """
        le constructeur
        @param filename le nom d'un fichier video
        """
        filename = unicode(filename,'utf8')
        self.filename=filename
        print "yyyyyyy", type(self.filename)
        self.filesize=os.path.getsize(filename.encode('utf8'))
        self.capture=cv.CreateFileCapture(self.filename.encode('utf8'))
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
            #print self.framecount, self.fps
            #print self.filesize, 1.0*self.filesize/self.framecount
            assert 1.0*self.filesize/self.framecount > 1800.0, "fichier aberrant en taille"
            self.ok=True
        except AssertionError:
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

