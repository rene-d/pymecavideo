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
from PyQt5.QtGui import QKeySequence, QIcon, QPixmap, QImage,QPainter, QCursor, QPen, QColor, QFont
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel,QWidget, QShortcut, QDesktopWidget, QLayout, QFileDialog, QTableWidgetItem, QInputDialog, QLineEdit, QMessageBox, QTableWidgetSelectionRange

from vecteur import vecteur
from zoom import Zoom_Croix
import os


class Label_Video(QLabel):
    def __init__(self, parent, app):
        QLabel.__init__(self, parent)
        self.parent = parent
        self.app = app
        self.setGeometry(QRect(0, 0, self.app.largeur, self.app.hauteur))
        self.setMinimumSize(QSize(640,480))
        self.liste_points = []
        self.app.dbg.p(1, "In : Label_Video, __init__")
        self.cropX2 = None
        self.cible_icon = os.path.join(self.app._dir("icones"), "curseur_cible.svg")
        pix = QPixmap(self.cible_icon).scaledToHeight(32, 32)
        self.cursor = QCursor(pix)
        self.setCursor(self.cursor)
        self.pos_zoom = vecteur(50, 50)
        self.zoom_croix = Zoom_Croix(self.app.ui.label_zoom, self.app)
        self.zoom_croix.hide()
        self.setMouseTracking(True)
        
        #####################TODO
        self.decal = vecteur(0, 0)  #if video is not 4:3, center video

        self.couleurs = ["red", "blue", "cyan", "magenta", "yellow", "gray", "green", "red", "blue", "cyan", "magenta",
                         "yellow", "gray", "green"]

    def sizeHint(self):

        return QSize(self.app.largeur, self.app.hauteur)

    def heightForWidth(self, width):

        return QtGui.QLabel.heightForWidth(self, width)

    def reinit(self):
        try:
            del self.zoom_croix
        except:
            pass
        self.met_a_jour_crop()
        self.setMouseTracking(True)

    def storePoint(self, point):
        if self.app.lance_capture == True:
            self.app.enregistre_dans_listePoints(point)
            self.liste_points.append(point)
            self.pos_avant = self.pos_zoom
            self.app.clic_sur_video.emit()
            self.met_a_jour_crop(self.pos_zoom)
            self.update()

    def mouseReleaseEvent(self, event):
        self.storePoint(vecteur(event.x(), event.y()))


    def enterEvent(self, event):
        if self.app.lance_capture == True and self.app.auto == False:  # ne se lance que si la capture est lancée
            pix = QPixmap(self.cible_icon).scaledToHeight(32, 32)
            self.cursor = QCursor(pix)
            self.setCursor(self.cursor)
        else:
            self.setCursor(Qt.ArrowCursor)
            
        
    def maj(self):
        self.app.dbg.p(1, "rentre dans 'label_video.maj'")
        self.setGeometry(QRect(0, 0, self.app.largeur, self.app.hauteur))

    def met_a_jour_crop(self, pos_zoom = vecteur(50,50)):
        self.fait_crop(pos_zoom)
        self.app.ui.label_zoom.setPixmap(self.cropX2)

    def leaveEvent(self, event):
        if self.app.lance_capture == True:
            self.cache_zoom()
        self.app.gardeLargeur()    
        
    def mouseMoveEvent(self, event):
        if self.app.lance_capture == True and self.app.auto == False:  # ne se lance que si la capture est lancée
            self.zoom_croix.show()
            self.pos_zoom = vecteur(event.x(), event.y())
            self.fait_crop(self.pos_zoom)
            self.app.ui.label_zoom.setPixmap(self.cropX2)

    def cache_zoom(self):
        pass

    def paintEvent(self, event):
        if self.app.a_une_image : 
            if self.app.echelle_faite and self.app.lance_capture:
                self.fait_crop(self.pos_zoom)
                self.app.ui.label_zoom.setPixmap(self.cropX2)

            self.painter = QPainter()
            self.painter.begin(self)
            try:
                self.painter.drawPixmap(self.decal.x(), self.decal.y(), self.pixmap())
            except TypeError:  # pixmap is not declare yet
                pass

            ############################################################
            # paint the origin
            
            self.painter.setPen(Qt.green)
            try : 
                self.painter.drawLine(self.app.origine.x() - 5, self.app.origine.y(), self.app.origine.x() + 5, self.app.origine.y())
                self.painter.drawLine(self.app.origine.x(), self.app.origine.y() - 5, self.app.origine.x(), self.app.origine.y() + 5)
                self.painter.drawText(self.app.origine.x(), self.app.origine.y() + 15, "O")
            except : 
                pass

            ############################################################
            #draw points
            self.app.dbg.p(5, "In label_video, paintEvent, self.app.points :%s" % self.app.points)
            cptr_point = 0
            for points in self.app.listePoints:  #all points clicked are stored here, but updated every "number of point to click" frames
                color = cptr_point%self.app.nb_de_points
                cptr_point+=1
                point = points[2]
                if type(point) != type(""):
                    self.painter.setPen(QColor(self.couleurs[color]))
                    self.painter.setFont(QFont("", 10))
                    self.painter.translate(point.x(), point.y())
                    self.painter.drawLine(-2, 0, 2, 0)
                    self.painter.drawLine(0, -2, 0, 2)
                    self.painter.translate(-10, +10)
                    self.painter.drawText(0, 0, str(color+1 ))

                    self.painter.translate(-point.x() + 10, -point.y() - 10)

            ############################################################
            #paint repere
            self.painter.setPen(Qt.green)
            self.painter.translate(0, 0)
            try : 
                self.painter.translate(self.app.origine.x(), self.app.origine.y())
            except AttributeError: 
                pass
            p1 = QPoint(self.app.sens_X * (-40), 0)
            p2 = QPoint(self.app.sens_X * (40), 0)
            p3 = QPoint(self.app.sens_X * (36), 2)
            p4 = QPoint(self.app.sens_X * (36), -2)
            self.painter.scale(1, 1)
            self.painter.drawPolyline(p1, p2, p3, p4, p2)
            self.painter.rotate(self.app.sens_X * self.app.sens_Y * (-90))
            self.painter.drawPolyline(p1, p2, p3, p4, p2)
            ############################################################

            self.painter.end()


    def fait_crop(self, p):
        rect = QRect(p.x() - 25, p.y() - 25, 50, 50)
        crop = self.app.imageAffichee.copy(rect)
        self.cropX2 = QPixmap.fromImage(crop.scaled(100, 100, Qt.KeepAspectRatio))
