#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import threading
import os.path

import cv


class film:
    """
    Une classe pour accéder aux images d'un film
    """

    def __init__(self, filename):
        """
        le constructeur
        @param filename le nom d'un fichier video
        """
        self.filename = filename
        self.filesize = os.path.getsize(filename)
        self.capture = cv.CreateFileCapture(self.filename)
        t = threading.Thread(target=self.autoTest)
        t.start()
        t.join(5.0)  # attente de 5 secondes au plus


    def autoTest(self):
        self.ok = False
        try:
            self.data = cv.GetCaptureProperty(self.capture, cv.CV_CAP_PROP_POS_MSEC)
            print "CV_CAP_PROP_POS_MSEC : ", self.data
            self.data = cv.GetCaptureProperty(self.capture, cv.CV_CAP_PROP_POS_FRAMES)
            print "CV_CAP_PROP_POS_FRAMES : ", self.data
            self.data = cv.GetCaptureProperty(self.capture, cv.CV_CAP_PROP_POS_AVI_RATIO)
            print "CV_CAP_PROP_POS_AVI_RATIO : ", self.data
            self.data = cv.GetCaptureProperty(self.capture, cv.CV_CAP_PROP_FRAME_WIDTH)
            print "CV_CAP_PROP_FRAME_WIDTH : ", self.data
            self.data = cv.GetCaptureProperty(self.capture, cv.CV_CAP_PROP_FRAME_HEIGHT)
            print "CV_CAP_PROP_FRAME_HEIGHT : ", self.data
            self.data = cv.GetCaptureProperty(self.capture, cv.CV_CAP_PROP_FPS)
            print "CV_CAP_PROP_FPS : ", self.data
            self.data = cv.GetCaptureProperty(self.capture, cv.CV_CAP_PROP_FOURCC)
            print "CV_CAP_PROP_FOURCC : ", self.data
            self.data = cv.GetCaptureProperty(self.capture, cv.CV_CAP_PROP_FRAME_COUNT)
            print "CV_CAP_PROP_FRAME_COUNT : ", self.data
            self.ok = True
        except:
            pass

    def __int__(self):
        return int(self.ok)

    def __nonzero__(self):
        return self.ok


if __name__ == '__main__':
    if len(sys.argv) > 1:
        vidfile = sys.argv[1]
        if film(vidfile):
            sys.exit(0)
        else:
            sys.exit(1)

