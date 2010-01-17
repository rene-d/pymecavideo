# -*- coding: utf-8 -*-
from vecteur import vecteur

from math import sqrt
from PyQt4.QtCore import *
from PyQt4.QtGui import *

class Label_Origine_Trace(QLabel):
    def __init__(self, parent, origine):
        QLabel.__init__(self, parent)
        self.parent = parent
        self.setGeometry(QRect(0,0,640,480))
        self.setAutoFillBackground(False)
        self.origine = origine
        self.setMouseTracking(True)
    def mouseMoveEvent(self, event):
        event.ignore()
    def mouseReleaseEvent(self, event):
        event.ignore()
    def paintEvent(self, event):
        painter = QPainter()
        painter.begin(self)
        #painter.drawPixmap(0,0,self.pix)
        painter.setPen(Qt.green)
        painter.drawLine(self.origine.x()-5, self.origine.y(), self.origine.x()+5, self.origine.y())
        painter.drawLine(self.origine.x(), self.origine.y()-5, self.origine.x(), self.origine.y()+5)
        painter.drawText(self.origine.x(), self.origine.y()+15, "O")
        painter.end()


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
        try :
            self.app.origine_trace.hide()
            del self.app.origine_trace
        except :
            pass
        self.app.origine_trace = Label_Origine_Trace(parent=self.parent, origine=self.app.origine)
        self.app.origine_trace.show()
        #print self.app.origine
        self.close()