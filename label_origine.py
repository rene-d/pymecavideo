# -*- coding: utf-8 -*-
from vecteur import vecteur

from math import sqrt
from PyQt4.QtCore import *
from PyQt4.QtGui import *

class Label_Origine(QLabel):
    def __init__(self, parent,app):
        QLabel.__init__(self, parent)
        self.parent = parent
        self.setGeometry(QRect(0,0,640,480))
        self.setAutoFillBackground(False)
        self.app = app
        self.setCursor(Qt.CrossCursor)
        

    def mouseReleaseEvent(self, event):
        self.app.origine = vecteur(event.x() + 1, event.y() + 1)
        
        print self.app.origine
        self.close()