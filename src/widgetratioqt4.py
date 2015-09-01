# -*- coding: utf-8 -*-
import sys
#from PyQt5.QtCore import *
#from PyQt5.QtGui import *
#from PyQt5.QtWidgets import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *

class widgetratio(QTabWidget):
    def __init__(self, parent):
        QTabWidget.__init__(self,parent)
        self.setMinimumSize(QSize(876, 618))

        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(True)
        self.setSizePolicy(sizePolicy)

class centralwidgetratio(QWidget):
    def __init__(self, parent):
        QTabWidget.__init__(self,parent)
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.setMinimumSize(QSize(876, 615))
        self.parent = parent
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(True)
        self.setSizePolicy(sizePolicy)
        self.setGeometry(0,15,876,615)

    def heightForWidth(self, w):
        if self.width() <875 or self.height() < 615:
            return 615
        else :
            try :
                hauteur = int((self.width()-self.parent.decalw)/self.parent.ratio)+self.parent.decalh
                return hauteur if hauteur >= 615 else 615
            except AttributeError:
                return 615

    def sizeHint(self):
        w = self.width()
        return QSize( w, self.heightForWidth(w) )

    def resizeEvent(self, e):
        #QApplication.instance().processEvents()
        self.setFixedHeight(self.heightForWidth(self.width()))