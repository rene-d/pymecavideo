# -*- coding: utf-8 -*-
from vecteur import vecteur

from math import sqrt
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from zoom import Zoom_Croix


class Label_Origine(QLabel):
    def __init__(self, parent,app):
        QLabel.__init__(self, parent)
        self.parent = parent
        self.setGeometry(QRect(0,0,640,480))
        self.setAutoFillBackground(False)
        self.app = app
        self.setCursor(Qt.CrossCursor)
        self.cropX2=None
        self.zoom_croix = Zoom_Croix(self.app.ui.label_zoom)
        self.zoom_croix.hide()
        self.setMouseTracking(True)
        
    def mouseMoveEvent(self, event):
        self.zoom_croix.show()
        self.pos=vecteur(event.x(), event.y())
        self.fait_crop(self.pos)
        self.app.ui.label_zoom.setPixmap(self.cropX2)
        
    def fait_crop(self, p):
        rect = QRect(p.x()-25,p.y()-25,50,50)
        crop = self.app.image_640_480.copy(rect)
        self.cropX2=QPixmap.fromImage(crop.scaled(100,100,Qt.KeepAspectRatio))


    def mouseReleaseEvent(self, event):
        self.app.origine = vecteur(event.x() + 1, event.y() + 1)
        
        #try :
            #self.app.origine_trace.hide()
            #del self.app.origine_trace
        #except :
            #pass
        self.zoom_croix.hide()
        self.app.ui.label_zoom.setPixmap(QPixmap(None))
        del self.zoom_croix
        self.app.emit(SIGNAL('change_axe_origine()'))

        self.close()