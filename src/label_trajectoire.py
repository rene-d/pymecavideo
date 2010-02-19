#-*- coding: utf-8 -*-
from PyQt4.QtCore import *
from PyQt4.QtGui import *

class Label_Trajectoire(QLabel):
    def __init__(self, parent, app):
        QLabel.__init__(self,parent)
        self.app=app
        self.setGeometry(QRect(0,0,640,480))
        self.setCursor(Qt.ArrowCursor)
        self.setAutoFillBackground(True)
        self.setMouseTracking(1)

    def mouseMoveEvent(self, event):
        self.app.traiteSouris(event.pos())
    
    def paintEvent(self,event):
        self.painter = QPainter()
        self.painter.begin(self)
        self.painter.fillRect(QRect(0,0,640,480),QColor("grey"))
        self.painter.end()
        
