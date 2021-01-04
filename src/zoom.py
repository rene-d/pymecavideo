# -*- coding: utf-8 -*-

"""
    videotraj, a module for pymecavideo:
      a program to track moving points in a video frameset
      
    Copyright (C) 2007 Jean-Baptiste Butet <ashashiwa@gmail.com>

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from PyQt5.QtCore import QThread, pyqtSignal, QLocale, QTranslator, Qt, QSize, QTimer, QObject, QRect, QPoint, QPointF
from PyQt5.QtGui import QKeySequence, QIcon, QPixmap, QImage,QPainter, QCursor, QPen, QColor
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel,QWidget, QShortcut, QDesktopWidget, QLayout, QFileDialog, QTableWidgetItem, QInputDialog, QLineEdit, QMessageBox, QTableWidgetSelectionRange


class Zoom_Croix(QWidget):
    def __init__(self, parent, app):
        QWidget.__init__(self, parent)
        self.parent = parent
        self.app = app

        self.setEnabled(True)
        self.setGeometry(QRect(0, 0, 100, 100))
        self.setAutoFillBackground(False)

    def paintEvent(self, event):
        painter = QPainter()
        painter.begin(self)
        painter.setPen(Qt.red)
        painter.drawLine(50, 0, 50, 45)
        painter.drawLine(50, 55, 50, 100)
        painter.drawLine(0, 50, 45, 50)
        painter.drawLine(55, 50, 100, 50)

        painter.setPen(QPen(QColor(255,64,255),1)) # fixe la couleur du crayon et la largeur pour le dessin - forme compactée
                # cf QPen(QBrush brush, float width, Qt.PenStyle style = Qt.SolidLine, Qt.PenCapStyle cap = Qt.SquareCap, Qt.PenJoinStyle join = Qt.BevelJoin)
        painter.drawEllipse(QPointF(50,50),5,5)
