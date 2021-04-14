import sys
from PyQt5.QtCore import QThread, pyqtSignal, QLocale, QTranslator, Qt, QSize, QTimer
from PyQt5.QtGui import QKeySequence, QIcon, QPixmap, QImage
from PyQt5.QtWidgets import QTabWidget, QApplication, QMainWindow, QWidget, QShortcut, QDesktopWidget, QLayout, QFileDialog, QTableWidgetItem, QInputDialog, QLineEdit, QMessageBox, QTableWidgetSelectionRange, QSizePolicy

class widgetratio(QTabWidget):
    def __init__(self, parent):
        QTabWidget.__init__(self,parent)
        self.setMinimumSize(QSize(800, 600))

        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(True)
        self.setSizePolicy(sizePolicy)

class centralwidgetratio(QWidget):
    def __init__(self, parent):
        QTabWidget.__init__(self,parent)
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.setMinimumSize(QSize(800, 600))
        self.parent = parent
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
    #    sizePolicy.setHeightForWidth(True)
        self.setSizePolicy(sizePolicy)
        self.setGeometry(0,15,800,600)

    def heightForWidth(self, w):
        if self.width() < 875 or self.height() < 615:
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

        
